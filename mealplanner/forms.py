from django import forms
    
def recipe_name_form_factory(initName='',initServings=1,initInstructions=''):
    class RecipeNameForm(forms.Form):
        name = forms.CharField(required=True,initial=initName)
        servings = forms.IntegerField(min_value=1,initial=initServings)
        instructions = forms.CharField(required=False,initial=initInstructions,
                                 widget=forms.Textarea(attrs={'cols': 20, 'rows': 6}))
    return RecipeNameForm



def info_form_factory(user):
    class AuthorInfoForm(forms.Form):
        username = forms.CharField(initial=user.username)
        password = forms.CharField(label='New Password',widget=forms.PasswordInput,required=False)
        check = forms.CharField(label='Retype Password',widget=forms.PasswordInput,required=False)
        if(hasattr(user,'author') and user.author.defaultServings):
            ini = user.author.defaultServings
        else:
            ini = 4
        defaultServings = forms.IntegerField(min_value=1,initial=ini)
        
        def clean(self):
            cleaned_data = super(AuthorInfoForm, self).clean()
            if(cleaned_data.get("password") != cleaned_data.get("check")):
                raise forms.ValidationError('Passwords do not match')
            return cleaned_data
    return AuthorInfoForm