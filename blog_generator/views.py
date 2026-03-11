from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube
from django.conf import settings
import os
import assemblyai as aai
import openai
from .models import BlogPost







# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generator_blog(request):
    if request.method=='POST':
        try:
            data=json.loads(request.body)
            yt_link=data['link']
            # return JsonResponse({'content':yt_link})
            
        except(KeyError,json.JSONDecodeError):
            return JsonResponse({"error":"Invalid  data sent"}, status=400)
        
        #get title
        title=yt_title(yt_link)
        if not title:
            return JsonResponse({"error":"invalid youtube link or video not found"},status=400)
        
        
        #get transcript
        transcription=get_transcription(yt_link)
        if not transcription:
            return JsonResponse({"error":"failed to get transcript"},status=500)
        
        
        #use OpenAI to generate blog
        blog_content=generate_blog_from_transcritption(transcription)
        if not blog_content:
            return JsonResponse({"error":"failed to generate blog article"},status=500)
        
        
        
        
        #save blog article to database
        new_blog_artcile=BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )
        new_blog_artcile.save()
        
        
        
        #return blog article as a response
        return JsonResponse({"content":blog_content})
    else:
        return JsonResponse({"error":"Invalid request method"}, status=405)
def yt_title(link):
    try:
        yt=YouTube(link)
        title=yt.title
        return title
    except Exception as e:
        return None
  

def download_audio(link):
    yt=YouTube(link)
    video=yt.streams.filter(only_audio=True).first()
    out_file=video.download(output_path=settings.MEDIA_ROOT)
    base,ext=os.path.splitext(out_file)
    new_file=base+".mp3"
    os.rename(out_file,new_file)
    return new_file



def get_transcription(link):
   
    audio_file=download_audio(link)
    aai.settings.api_key="160449bfcaff4601a8bafb56d96b38d3"
    transcriber=aai.Transcriber()
    transcript=transcriber.transcribe(audio_file)
    
    return transcript.text
    

def generate_blog_from_transcritption(transcript):
    api_key = os.getenv('OPENAI_API_KEY')
    
    prompt=f"Based on the following transcript from a YouTube Video, write a comprehensive blog article,wite it based on the transcript, but do not make it look like YouTube video,make it look like a proper blog article:\n\n{transcript}\n\n article:"
    
    response=openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
    )
    generated_content=response.choices[0].text.strip()
    return generated_content



def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            Error_meassage = "Invalid username or password"
            return render(request, 'login.html', {'Error_meassage': Error_meassage})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email=request.POST['email']
        repeatepassword = request.POST['repeatpassword']
        
        if password == repeatepassword:
            try:
                user=User.objects.create_user(username,email,password)
                user.save()
                login(request,user)
                return redirect('/')
            except:
                Error_meassage="Error creating account"
                return render(request, 'signup.html', {'Error_meassage': Error_meassage})
                
        else:
            Error_meassage = "password not match"
            return render(request, 'signup.html', {'Error_meassage': Error_meassage})
            

    return render(request, 'signup.html')

def blog_list(request):
    blog_articles=BlogPost.objects.filter(user=request.user)
    
    return render(request,"all-blogs.html",{"blog_articles":blog_articles})

def blog_details(request,pk):
    blog_article_content=BlogPost.objects.get(id=pk)
    if request.user==blog_article_content.user:
        return render(request,"blog-details.html",{"blog_article_content":blog_article_content})
    else:
        return redirect("/")

@login_required
def user_logout(request):
    logout(request)
    return redirect('/')

