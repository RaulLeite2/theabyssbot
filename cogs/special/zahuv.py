import discord
from discord.ext import commands
import asyncio
import random
import json
from datetime import datetime, timedelta

# Zahuv: The Distant Lands of Zahuv
try:
    from cogs.rpg import CAPITAL_ZONE_ID
except Exception:
    CAPITAL_ZONE_ID = 0

class Zahuv(commands.Cog):
    """Background world manager for Zahuv: creates zones, spawns events and portals, expires zones.

    Behavior implemented:
    - Create a new zone every 3 minutes, up to 25 non-hub zones in Zahuv.
    - Every 1 minute attempt to spawn an event in zones without active events; events last 15 minutes.
    - Expire zones older than 3 days (remove zone, move users to capital).
    - In empty maps (no active events) there's a small chance to spawn a portal event.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._tasks = []
        # start background runner
        self.bot.loop.create_task(self._start())

    async def _start(self):
        await self.bot.wait_until_ready()
        self._tasks.append(self.bot.loop.create_task(self.zone_creator_loop()))
        self._tasks.append(self.bot.loop.create_task(self.event_creator_loop()))
        self._tasks.append(self.bot.loop.create_task(self.zone_expiry_loop()))
        self._tasks.append(self.bot.loop.create_task(self.zone_cleanup_loop()))

    async def cog_unload(self):
        for t in self._tasks:
            t.cancel()

    async def zone_creator_loop(self):
        """Creates zones every 3 minutes until there are 15 non-hub, non-hideout zones."""
        while not self.bot.is_closed():
            try:
                # count current non-hub, non-hideout zones (normal zones)
                count = await self.bot.db.fetchval(
                    "SELECT COUNT(*) FROM zone WHERE is_hub = FALSE AND is_hideout = FALSE"
                )
                if count is None:
                    count = 0
                
                # Create normal zones (2 names) up to 15
                if count < 15:
                    name = await self._generate_zone_name(is_hideout=False)
                    # Tier aleatório com variação: pode ser de 1 a 8, com chance de ser maior
                    # Base tier 1-4, mas pode ter "spike" para tiers mais altos
                    base_tier = random.randint(1, 4)
                    # 20% de chance de ser um tier superior (5-8)
                    if random.random() < 0.20:
                        tier = random.randint(5, 8)
                    else:
                        tier = base_tier
                    
                    await self.bot.db.execute(
                        "INSERT INTO zone (nome, tier, permanent, is_hub, is_hideout) VALUES ($1,$2,FALSE,FALSE,FALSE)",
                        name, tier
                    )
                
                # Also create some HO zones (3 names) for potential hideouts
                ho_count = await self.bot.db.fetchval(
                    "SELECT COUNT(*) FROM zone WHERE is_hideout = TRUE AND NOT EXISTS (SELECT 1 FROM hideouts h WHERE h.zone_id = zone.zone_id)"
                )
                if ho_count is None:
                    ho_count = 0
                
                # Keep 10 empty HO zones available
                if ho_count < 10:
                    name = await self._generate_zone_name(is_hideout=True)
                    # HO zones também têm tier aleatório com possibilidade de tier maior
                    base_tier = random.randint(1, 4)
                    # 30% de chance de ser tier superior para zonas de HO
                    if random.random() < 0.30:
                        tier = random.randint(5, 8)
                    else:
                        tier = base_tier
                    
                    await self.bot.db.execute(
                        "INSERT INTO zone (nome, tier, permanent, is_hub, is_hideout) VALUES ($1,$2,FALSE,FALSE,TRUE)",
                        name, tier
                    )
                
                await asyncio.sleep(180)  # 3 minutes
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(60)

    async def event_creator_loop(self):
        """Every minute create an event in zones without active events. Events last 15 minutes."""
        while not self.bot.is_closed():
            try:
                # pick zones without active event (only normal zones and hideouts with actual hideouts)
                rows = await self.bot.db.fetch(
                    """
                    SELECT zone_id, nome FROM zone z 
                    WHERE NOT EXISTS (SELECT 1 FROM events e WHERE e.zone_id = z.zone_id AND e.active = TRUE) 
                    AND is_hub = FALSE
                    AND (
                        is_hideout = FALSE 
                        OR EXISTS (SELECT 1 FROM hideouts h WHERE h.zone_id = z.zone_id)
                    )
                    """
                )
                for r in rows:
                    # small random chance to skip to avoid filling instantly
                    if random.random() < 0.5:
                        continue

                    # chance to spawn a portal instead of normal event if area empty
                    if random.random() < 0.05:
                        # portal event type = 3 (placeholder)
                        reward = {"portal": True}
                        await self.bot.db.execute(
                            "INSERT INTO events (type, zone_id, reward, active) VALUES ($1,$2,$3,TRUE)",
                            3, r["zone_id"], json.dumps(reward)
                        )
                    else:
                        # spawn normal event: type 1 (dungeon) or 2 (worldboss rare)
                        ev_type = 2 if random.random() < 0.08 else 1
                        reward = {"gold": random.randint(50, 500) * (1 if ev_type == 1 else 10), "xp": random.randint(20, 200)}
                        ev = await self.bot.db.fetchrow(
                            "INSERT INTO events (type, zone_id, reward, active) VALUES ($1,$2,$3,TRUE) RETURNING id",
                            ev_type, r["zone_id"], json.dumps(reward)
                        )
                        # schedule deactivation after 15 minutes
                        if ev:
                            self.bot.loop.create_task(self.deactivate_event_after(ev["id"], 15 * 60))

                await asyncio.sleep(60)  # 1 minute
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(30)

    async def zone_expiry_loop(self):
        """Delete zones older than 3 days (except hubs and hideouts with HO)."""
        while not self.bot.is_closed():
            try:
                cutoff = datetime.utcnow() - timedelta(days=3)
                # find old zones (exclude hideouts with actual hideouts)
                rows = await self.bot.db.fetch(
                    """
                    SELECT zone_id FROM zone 
                    WHERE is_hub = FALSE 
                    AND created_at < $1
                    AND (
                        is_hideout = FALSE 
                        OR NOT EXISTS (SELECT 1 FROM hideouts h WHERE h.zone_id = zone.zone_id)
                    )
                    """, 
                    cutoff
                )
                for r in rows:
                    zid = r["zone_id"]
                    # move players to capital
                    try:
                        await self.bot.db.execute("UPDATE users SET zona_id = $1 WHERE zona_id = $2", CAPITAL_ZONE_ID, zid)
                        await self.bot.db.execute("DELETE FROM events WHERE zone_id = $1", zid)
                        await self.bot.db.execute("DELETE FROM zone WHERE zone_id = $1", zid)
                    except Exception:
                        pass
                # run expiry every hour
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(60)

    async def zone_cleanup_loop(self):
        """Delete zones without players for 15 minutes (except hubs and hideouts with HO)."""
        while not self.bot.is_closed():
            try:
                cutoff = datetime.utcnow() - timedelta(minutes=15)
                # find zones without players and older than 15 minutes
                rows = await self.bot.db.fetch(
                    """
                    SELECT z.zone_id, z.nome FROM zone z
                    WHERE z.is_hub = FALSE
                    AND z.created_at < $1
                    AND NOT EXISTS (SELECT 1 FROM users u WHERE u.zona_id = z.zone_id)
                    AND (
                        z.is_hideout = FALSE 
                        OR NOT EXISTS (SELECT 1 FROM hideouts h WHERE h.zone_id = z.zone_id)
                    )
                    """,
                    cutoff
                )
                
                for r in rows:
                    zid = r["zone_id"]
                    try:
                        # delete events and zone
                        await self.bot.db.execute("DELETE FROM events WHERE zone_id = $1", zid)
                        await self.bot.db.execute("DELETE FROM zone WHERE zone_id = $1", zid)
                    except Exception:
                        pass
                
                # run cleanup every 5 minutes
                await asyncio.sleep(300)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(60)

    async def deactivate_event_after(self, event_id: int, seconds: int):
        await asyncio.sleep(seconds)
        try:
            await self.bot.db.execute("UPDATE events SET active = FALSE WHERE id = $1", event_id)
        except Exception:
            pass

    async def _generate_zone_name(self, is_hideout: bool = False) -> str:
        """Generate a reasonably unique zone name.
        
        Args:
            is_hideout: If True, generates 3-word names for HO zones (e.g. "Ai'rathel Sombrio Pântano")
                       If False, generates 2-word names for normal zones (e.g. "Sombrio Pântano")
        """
        adjectives = ["Sombrio", "Velho", "Desolado", "Brumoso", "Silente", "Quebrado", "Aurora", 
                      "Eterno", "Perdido", "Gelado", "Ardente", "Místico", "Profundo", "Árido"]
        nouns = ["Pântano", "Cume", "Abismo", "Vale", "Ruína", "Fenda", "Bosque", 
                 "Deserto", "Floresta", "Caverna", "Templo", "Fortaleza", "Porto", "Montanha"]
        
        # HO prefixes (mystical names)
        ho_prefixes = ["Ai'rathel", "Et'morun", "Al'therion", "Jo'valdris", "Ka'velmir", 
                       "Lu'rathis", "Xe'morven", "Ty'drakkar", "Ba'korath", "Vi'therax"]
        
        for _ in range(10):
            if is_hideout:
                # 3-word name: Prefix + Adjective + Noun
                prefix = random.choice(ho_prefixes)
                name = f"{prefix} {random.choice(adjectives)} {random.choice(nouns)}"
            else:
                # 2-word name: Adjective + Noun
                name = f"{random.choice(adjectives)} {random.choice(nouns)}"
            
            exists = await self.bot.db.fetchval("SELECT 1 FROM zone WHERE nome = $1", name)
            if not exists:
                return name
        
        # fallback with timestamp
        prefix_str = random.choice(ho_prefixes) + " " if is_hideout else ""
        return f"{prefix_str}Portal de Zahuv {int(datetime.utcnow().timestamp())}"

async def setup(bot: commands.Bot):
    cog = Zahuv(bot)
    await bot.add_cog(cog)
