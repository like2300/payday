from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from core.models import Fundraiser, Like

register = template.Library()

@register.simple_tag
def get_content_type_id(obj):
    if not obj:
        return ""
    return ContentType.objects.get_for_model(obj).id

@register.simple_tag
def get_likes_count(obj):
    if not obj:
        return 0
    content_type = ContentType.objects.get_for_model(obj)
    return Like.objects.filter(content_type=content_type, object_id=obj.id).count()

@register.simple_tag
def has_user_liked(obj, user):
    if not user.is_authenticated or not obj:
        return False
    content_type = ContentType.objects.get_for_model(obj)
    return Like.objects.filter(content_type=content_type, object_id=obj.id, user=user).exists()

@register.simple_tag(takes_context=True)
def get_categories_for_sidebar(context):
    request = context.get('request')
    if not request:
        return ""

    categories = Fundraiser.CATEGORY_CHOICES
    selected_category = request.GET.get('category', '')
    
    icons = {
        'birthday': 'celebration',
        'wedding': 'favorite',
        'graduation': 'school',
    }

    html = []
    
    # Add Vote manually as requested
    vote_categories = [
        ('vote', 'Vote', 'how_to_reg', reverse('vote_list')),
    ]
    
    for code, name, icon, url in vote_categories:
        is_active = request.resolver_match.url_name in ['vote_list', 'vote_detail'] if code == 'vote' else False
        active_class = "text-white bg-white/10 shadow-lg shadow-white/5" if is_active else "text-gray-400 hover:text-white hover:bg-white/5"
        
        item_html = f'''
            <li>
                <a href="{url}"
                   class="nav-item flex items-center gap-4 transition-colors py-3 px-4 rounded-xl {active_class}">
                    <span class="material-icons text-lg">{icon}</span>
                    <span class="nav-label font-bold text-sm">{name}</span>
                </a>
            </li>
        '''
        html.append(item_html)

    # Add spacing/divider
    html.append('<li class="my-4 border-t border-white/5"></li>')

    for code, name in categories:
        is_active = selected_category == code
        active_class = "text-white bg-white/10 shadow-lg shadow-white/5" if is_active else "text-gray-400 hover:text-white hover:bg-white/5"
        icon = icons.get(code, 'label')
        
        url = f"{reverse('fundraiser_list')}?category={code}"
        
        item_html = f'''
            <li>
                <a href="{url}"
                   class="nav-item flex items-center gap-4 transition-colors py-3 px-4 rounded-xl {active_class}">
                    <span class="material-icons text-lg">{icon}</span>
                    <span class="nav-label font-bold text-sm">{name}</span>
                </a>
            </li>
        '''
        html.append(item_html)
        
    return mark_safe("".join(html))

@register.filter
def first_part(value):
    """Returns the first part of a string split by comma."""
    if not value:
        return ""
    return str(value).split(',')[0]
