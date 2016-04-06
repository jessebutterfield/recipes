from django import forms
    
def recipe_name_form_factory(initName='',initServings=1,initInstructions=''):
    class RecipeNameForm(forms.Form):
        name = forms.CharField(required=True,initial=initName)
        servings = forms.IntegerField(min_value=1,initial=initServings)
        instructions = forms.CharField(required=False,initial=initInstructions,
                                 widget=forms.Textarea(attrs={'cols': 20, 'rows': 6}))
    return RecipeNameForm