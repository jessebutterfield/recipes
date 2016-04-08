from django import forms
from .models import Author, day_dictionary
from django.contrib.auth.models import User
    
def recipe_name_form_factory(initName='',initServings=1,initInstructions=''):
    class RecipeNameForm(forms.Form):
        name = forms.CharField(required=True,initial=initName)
        servings = forms.IntegerField(min_value=1,initial=initServings)
        instructions = forms.CharField(required=False,initial=initInstructions,
                                 widget=forms.Textarea(attrs={'cols': 20, 'rows': 6}))
    return RecipeNameForm

def signup_form():
    class UserForm(forms.Form):
        username = forms.CharField()
        password = forms.CharField(label='New Password',widget=forms.PasswordInput)
        check = forms.CharField(label='Retype Password',widget=forms.PasswordInput)
        email = forms.EmailField(label='Email address')
        
        def clean(self):
            cleaned_data = super(UserForm, self).clean()
            if(cleaned_data.get("password") != cleaned_data.get("check")):
                raise forms.ValidationError('Passwords do not match')
            users = User.objects.filter(username = cleaned_data.get('username'))
            if users.exists():
                raise forms.ValidationError('User name already in use')
            return cleaned_data
    return UserForm 



def info_form_factory(user):
    class AuthorInfoForm(forms.Form):
        username = forms.CharField(initial=user.username)
        password = forms.CharField(label='New Password',widget=forms.PasswordInput,required=False)
        check = forms.CharField(label='Retype Password',widget=forms.PasswordInput,required=False)
        author,_ = Author.objects.get_or_create(user=user)
        defaultServings = forms.IntegerField(min_value=1,initial=author.defaultServings)
        firstDayOfWeek = forms.ChoiceField(choices = day_dictionary, initial = author.firstDayOfWeek)
        
        def clean(self):
            cleaned_data = super(AuthorInfoForm, self).clean()
            if(cleaned_data.get("password") != cleaned_data.get("check")):
                raise forms.ValidationError('Passwords do not match')
            return cleaned_data
    return AuthorInfoForm