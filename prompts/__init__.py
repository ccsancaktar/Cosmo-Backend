"""
Çok dilli prompt sistemi
Desteklenen diller: Türkçe (tr), İngilizce (en), Almanca (de)
"""

from .multilingual import get_prompt_by_language, SUPPORTED_LANGUAGES

__all__ = ['get_prompt_by_language', 'SUPPORTED_LANGUAGES']
