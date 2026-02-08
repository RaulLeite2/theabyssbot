"""
Sistema de logging customizado com visual clean
Remove cores do terminal e adiciona emojis informativos
"""
import logging


class CleanFormatter(logging.Formatter):
    """Formatter limpo sem cores vermelhas chatas"""
    
    # Mapeia níveis de log para emojis
    EMOJI_MAP = {
        "DEBUG": "🔍",
        "INFO": "ℹ",
        "WARNING": "⚠",
        "ERROR": "✗",
        "CRITICAL": "🔥"
    }
    
    # Prefixos limpos por componente
    PREFIX_MAP = {
        "theabyssbot": "BOT",
        "discord": "DISC",
        "discord.gateway": "GATE",
        "discord.client": "CLIENT",
        "discord.http": "HTTP",
        "asyncpg": "DB",
        "asyncio": "ASYNC"
    }
    
    def format(self, record):
        # Pega emoji apropriado
        emoji = self.EMOJI_MAP.get(record.levelname, "•")
        
        # Simplifica nome do logger
        logger_name = record.name
        prefix = self.PREFIX_MAP.get(logger_name, logger_name.upper()[:8])
        
        # Mensagem limpa
        msg = record.getMessage()
        
        # Para erros, adiciona traceback de forma mais limpa
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        
        # Formato final limpo
        if record.levelno >= logging.ERROR:
            # Erros ficam mais destacados mas sem cor vermelha
            return f"[{prefix}] {emoji} {msg}"
        elif record.levelno == logging.WARNING:
            return f"[{prefix}] {emoji} {msg}"
        elif record.levelno == logging.DEBUG:
            # Debug mais discreto
            return f"[{prefix}] 🔍 {msg}"
        else:
            # Info normal
            return f"[{prefix}] {emoji} {msg}"


def setup_clean_logging(level=logging.INFO):
    """
    Configura logging com visual limpo
    """
    # Remove handlers antigos
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    
    # Cria novo handler com formatter limpo
    handler = logging.StreamHandler()
    handler.setFormatter(CleanFormatter())
    
    # Configura root logger
    root.setLevel(level)
    root.addHandler(handler)
    
    # Ajusta níveis de loggers específicos para reduzir ruído
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("discord.client").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Bot logger fica em INFO
    logging.getLogger("theabyssbot").setLevel(level)


def print_startup_header():
    """Cabeçalho bonito de inicialização"""
    print("\n" + "═" * 60)
    print("▣ THE ABYSS BOT :: Initializing")
    print("═" * 60)


def print_startup_footer():
    """Rodapé de inicialização"""
    print("═" * 60)
    print("▣ THE ABYSS BOT :: Ready")
    print("═" * 60 + "\n")
