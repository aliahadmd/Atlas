from django import template
from django.utils.safestring import mark_safe
import markdown2
import bleach

register = template.Library()

@register.filter
def getattribute(obj, attr):
    return getattr(obj, attr, '')

@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    # Convert Markdown to HTML
    html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables'])
    
    # Sanitize the HTML to prevent XSS attacks
    allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'ul', 'ol', 'li', 'code', 'pre', 'blockquote', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'br']
    allowed_attributes = {'a': ['href', 'title'], 'th': ['colspan'], 'td': ['colspan']}
    cleaned_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
    
    # Replace newlines with <br> tags to preserve line breaks
    cleaned_html = cleaned_html.replace('\n', '<br>')
    
    return mark_safe(cleaned_html)