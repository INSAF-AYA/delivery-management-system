from database.models import Agent


def user_context(request):
    """Add logged-in user info to template context."""
    context = {
        'logged_in_user': None,
        'logged_in_role': None,
    }
    
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    
    if user_id and role:
        try:
            agent = Agent.objects.get(agent_id=user_id)
            context['logged_in_user'] = agent
            context['logged_in_role'] = role.capitalize()
        except Agent.DoesNotExist:
            pass
    
    return context
