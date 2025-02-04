from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from .models import CustomUser
import requests
# Create your views here.


def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print('-------email and password-------', email,'------------', password)


        user = EmailBackend.authenticate(request, username=request.POST.get(
            'email'), password=request.POST.get('password'))
        
        if user != None:
            login(request, user)
            if user.user_type == '1':
                print('-------admin-------')
                return redirect(reverse("adminDashboard"))
            else:
                print('-------voter-------')
                return redirect(reverse("voterDashboard"))
        else:
            api_url = "http://localhost:8000/api/election/verifyUser"
            response = requests.post(api_url, json={"email": email})
            print('--------------first response----------------', response)
            if response.status_code == 200:
                data = response.json()
                print('--------second--------', data)
                if data.get("status") == 2:
                    messages.error(request, "Invalid credentials")
                    print('---------third--------')
                    return redirect("/")
                
                else:
                    new_user = CustomUser.objects.create(
                        email=data["email"],
                        username=data.get("username", email),  # Default to email if username is missing
                        password=make_password(password),  # Hash password before saving
                        first_name=data.get("name", ""),
                        last_name=data.get("last_name", ""),
                        user_type='2'
                    )
                    print('---------------fourth----------')
                    login(request, new_user)
                    return redirect(reverse("voterDashboard"))
            print('----------------fifth---------------')
            messages.error(request, "Invalid details")
            return redirect("/")

    return render(request, "voting/login.html", context)


def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        'form1': userForm,
        'form2': voterForm
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "Account created. You can login now!")
            return redirect(reverse('account_login'))
        else:
            messages.error(request, "Provided data failed validation")
            # return account_login(request)
    return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting us!")
    else:
        messages.error(
            request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))


