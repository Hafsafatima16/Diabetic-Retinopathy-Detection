from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth import login
from django.utils import timezone
from mainapp.models import *
from userapp.models import *
from adminapp.models import *
import pytz
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
import numpy as np
from .models import Dataset
import os
import base64
import cv2
from adminapp.models import  Inception, Resonet, Mobilenet
# Create your views here.

def user_dashboard(req):
    images_count =  User.objects.all().count()
    print(images_count)
    user_id = req.session["User_id"]
    user = User.objects.get(User_id = user_id)
    
    if user.Last_Login_Time is None:
        IST = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(IST).time()
        user.Last_Login_Time = current_time_ist
        user.save()
    return render(req,'user/user-dashboard.html', {'detect' : images_count, 'la' : user})



# Function to load and predict with a given model
def predict_image_class(image_path, loaded_model):
    img = image.load_img(image_path, target_size=(512, 512))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img / 255.0

    predictions = loaded_model.predict(img)
    class_index = np.argmax(predictions)
    class_probability = float(predictions[0][class_index])  # Convert to float

    class_labels = ['No_DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']
    predicted_label = class_labels[class_index]

    return predicted_label, class_probability


# Function to generate colorized RGB image
def generate_rgb_image(image_path):
    gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    color_image = cv2.applyColorMap(gray_image, cv2.COLORMAP_JET)
    rgb_image_path = os.path.splitext(image_path)[0] + '_colorized.jpg'
    cv2.imwrite(rgb_image_path, color_image)

    return rgb_image_path

# Function to generate segmented image
def generate_segmented_image(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
    segmented_image_path = os.path.splitext(image_path)[0] + '_segmented.jpg'
    cv2.imwrite(segmented_image_path, binary_image)
    return segmented_image_path

# View function to handle user input and prediction
def user_predict(request):
    if request.method == "POST" and request.FILES.get("img"):
        try:
            model_type = "Ensemble_Model"
            uploaded_file = request.FILES["img"]
            image_path = default_storage.save(uploaded_file.name, uploaded_file)

            # Load the appropriate model based on model_type
            if model_type == "Inception":
                model_file = 'model_retina.h5'
                loaded_model = load_model(model_file)
                model_info = Inception.objects.latest('User_id')
            elif model_type == "Ensemble_Model":
                model_file = 'resnet50_model.h5'
                loaded_model = load_model(model_file)
                model_info = Resonet.objects.latest('User_id')
            elif model_type == "Mobilenet":
                model_file = 'drdMbNetV2.h5'
                loaded_model = load_model(model_file)
                model_info = Mobilenet.objects.latest('User_id')
            else:
                raise ValueError("Select a valid Model")

            # Predict image class
            predicted_label, class_probability = predict_image_class(default_storage.path(image_path), loaded_model)

            # Process images and save to session
            uploaded_image_path = default_storage.path(image_path)
            rgb_image_path = generate_rgb_image(uploaded_image_path)
            segmented_image_path = generate_segmented_image(uploaded_image_path)

            # Encode images to base64
            with open(uploaded_image_path, "rb") as img_file:
                uploaded_image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            with open(rgb_image_path, "rb") as img_file:
                rgb_image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            with open(segmented_image_path, "rb") as img_file:
                segmented_image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            # Save necessary session variables
            try:
                request.session["image_path"] = default_storage.url(image_path)
                request.session["predicted_label"] = predicted_label
                request.session["uploaded_image_base64"] = uploaded_image_base64
                request.session["segmented_image_base64"] = segmented_image_base64
                request.session["rgb_image_base64"] = rgb_image_base64

                if model_info:
                    request.session["model_name"] = model_info.Executed
                    request.session["model_accuracy"] = str(model_info.Model_accuracy)

            except SessionInterrupted:
                messages.error(request, "Session was interrupted. Please try again.")
                return redirect("user_predict")

            # Redirect to Classification_result view
            messages.success(request, "Detection Process Completed")
            return redirect("result")

        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"Error processing image: {str(e)}")

    return render(request, 'user/user-predict.html')


# View for displaying the result
def result(req):
    try:
        # Retrieve necessary data from session or other sources
        image_path = req.session.get("image_path", None)
        predicted_label = req.session.get("predicted_label", "Unknown")
        model_accuracy = req.session.get("model_accuracy", None)
        model_name = req.session.get("model_name", None)
        segmented_image_base64 = req.session.get("segmented_image_base64", None)
        uploaded_image_base64 = req.session.get("uploaded_image_base64", None)
        rgb_image_base64 = req.session.get("rgb_image_base64", None)

        # Check if required session variables are present
        if not all([image_path, predicted_label, model_accuracy, model_name,
                    segmented_image_base64, uploaded_image_base64, rgb_image_base64]):
            return HttpResponseServerError("Required data not found in session.")

        return render(req, 'user/user-result.html', {
            "image_path": image_path,
            "predicted_label": predicted_label,
            "model_accuracy": model_accuracy,
            "model_name": model_name,
            "rgb_image_base64": rgb_image_base64,
            "uploaded_image_base64": uploaded_image_base64,
            "segmented_image_base64": segmented_image_base64
        })
    except Exception as e:
        return HttpResponseServerError("An error occurred while displaying the result.")





def user_profile(req):
    user_id = req.session["User_id"]
    user = User.objects.get(User_id = user_id)
    if req.method == 'POST':
        user_name = req.POST.get('firstname')
        user_age = req.POST.get('age')
        user_phone = req.POST.get('phone')
        user_email = req.POST.get('email')
        user_address = req.POST.get("address")
        
        user.Full_name = user_name
        user.Age = user_age
        user.Address = user_address
        user.Phone_Number = user_phone
        user.Email=user_email
       

        if len(req.FILES) != 0:
            image = req.FILES['pic']
            user.Image = image
            user.Full_name = user_name
            user.Age = user_age
            user.Address = user_address
            user.Phone_Number = user_phone
            user.Email=user_email
            user.Address=user_address
            
            user.save()
            messages.success(req, 'Updated SUccessfully...!')
        else:
            user. Full_name = user_name
            user.Age = user_age
            user.save()
            messages.success(req, 'Updated SUccessfully...!')
            
    context = {"i":user}
    return render(req,'user/user-profile.html',context)
def user_feedback(req):
    id=req.session["User_id"]
    uusser=User.objects.get(User_id=id)
    if req.method == "POST":
        rating=req.POST.get("rating")
        review=req.POST.get("review")
        # print(sentiment)        
        # print(rating,feed)
        sid=SentimentIntensityAnalyzer()
        score=sid.polarity_scores(review)
        sentiment=None
        if score['compound']>0 and score['compound']<=0.5:
            sentiment='positive'
        elif score['compound']>=0.5:
            sentiment='very positive'
        elif score['compound']<-0.5:
            sentiment='very negative'
        elif score['compound']<0 and score['compound']>=-0.5:
            sentiment='negative'
        else :
            sentiment='neutral'
        Feedback.objects.create(Rating=rating, Review=review,Sentiment=sentiment, Reviewer=uusser)
        messages.success(req,'Feedback recorded')
        return redirect('user_feedback')
    return render(req,'user/user-feedback.html')
def user_logout(req):
    user_id = req.session["User_id"]
    user = User.objects.get(User_id = user_id)
    t = time.localtime()
    user.Last_Login_Time = t
    current_time = time.strftime('%H:%M:%S', t)
    user.Last_Login_Time = current_time
    current_date = time.strftime('%Y-%m-%d')
    user.Last_Login_Date = current_date
    user.save()
    messages.info(req, 'You are logged out..')
    return render(req,'user/main-login.html')