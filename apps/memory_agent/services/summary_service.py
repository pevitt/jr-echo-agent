from typing import List
from apps.memory_agent.selectors.message_selector import MessageSelector


class SummaryService:
    """Servicio para generar resúmenes y búsquedas de mensajes"""
    
    def __init__(self):
        self.selector = MessageSelector()
    
    def generate_summary(self, recipient: str, period: str) -> str:
        """Genera un resumen estructurado de las ideas del usuario"""
        messages = self.selector.get_messages_by_recipient(recipient, period)
        
        if not messages:
            return f"No hay ideas registradas para el período: {period}"
        
        # Organizar por temas
        themes = self._organize_by_themes(messages)
        
        # Construir resumen
        summary = f"📑 **Resumen de Ideas ({period})**\n\n"
        
        for theme, ideas in themes.items():
            summary += f"**{theme}:**\n"
            for idea in ideas[:3]:  # Máximo 3 ideas por tema
                summary += f"- {idea}\n"
            summary += "\n"
        
        summary += f"**Total de ideas:** {len(messages)}\n"
        summary += f"**Período:** {period}"
        
        return summary
    
    def search_messages(self, recipient: str, search_term: str) -> str:
        """Busca mensajes que contengan el término de búsqueda"""
        if not search_term:
            return "Por favor proporciona un término de búsqueda."
        
        messages = self.selector.search_messages(recipient, search_term)
        
        if not messages:
            return f"No se encontraron ideas relacionadas con '{search_term}'."
        
        result = f"🔍 **Resultados para '{search_term}':**\n\n"
        
        for message in messages:
            result += f"- {message.content[:100]}{'...' if len(message.content) > 100 else ''}\n"  # type: ignore
            result += f"  *{message.created_at.strftime('%d/%m/%Y %H:%M')}*\n\n"  # type: ignore
        
        return result
    
    def _organize_by_themes(self, messages: List) -> dict:
        """Organiza los mensajes por temas"""
        themes = {}
        
        for message in messages:
            content_lower = message.content.lower()  # type: ignore
            
            # Clasificación por palabras clave
            if any(word in content_lower for word in ['trabajo', 'proyecto', 'oficina', 'empresa']):
                theme = 'Trabajo'
            elif any(word in content_lower for word in ['personal', 'familia', 'amigos', 'casa']):
                theme = 'Personal'
            elif any(word in content_lower for word in ['idea', 'invento', 'crear', 'innovar']):
                theme = 'Ideas'
            elif any(word in content_lower for word in ['estudio', 'aprender', 'curso', 'libro']):
                theme = 'Educación'
            elif any(word in content_lower for word in ['salud', 'ejercicio', 'dieta', 'médico']):
                theme = 'Salud'
            else:
                theme = 'General'
            
            if theme not in themes:
                themes[theme] = []
            
            # Truncar contenido si es muy largo
            content = message.content[:100] + '...' if len(message.content) > 100 else message.content
            themes[theme].append(content)
        
        return themes
