from django import template

from ..views import updateRotateStateFlagFunction

register = template.Library()

#Sayfa Refresh olayları için update filtresi oluşturduk kendimize
def updateRotateStateFlag(value):
    #updateRotateStateFlagFunction(value)
    print("kkk")

register.filter('updateRotateStateFlag', updateRotateStateFlag)