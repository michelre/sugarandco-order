from django.shortcuts import render
from django.views import View
from .forms import LoginForm, SignUpForm
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect



# Create your views here.
class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        # Handle login logic here
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('orderapp:home')
        return render(request, 'login.html', {'form': form})
