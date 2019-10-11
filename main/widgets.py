from django.forms.widgets import Widget

class PlusMinusNumberInput(Widget):
    template_name = 'widget/plusminusinput.html'

    class Media:
        css = {'all': 'css/plusminusinput.css'}
        js = ('js/plusminusinput.js',)
    