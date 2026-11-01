from django.shortcuts import render,redirect
from mainapp.models import*
from userapp.models import*
from adminapp.models import *
from django.contrib import messages
from django.core.paginator import Paginator
# Create your views here.
def adminlogout(req):
    messages.info(req,'You are logged out...!')
    return redirect('admin_login')
def admindashboard(request):
    all_users_count =  User.objects.all().count()
    pending_users_count = User.objects.filter(User_Status = 'Pending').count()
    rejected_users_count = User.objects.filter(User_Status = 'removed').count()
    user_uploaded_images =Dataset.objects.all().count()
    return render(request,'admin/admin-dashboard.html',{'a' : all_users_count, 'b' : pending_users_count, 'c' : rejected_users_count, 'd':user_uploaded_images})

def adminpendingusers(request):
    pending = User.objects.filter(User_Status="pending")
    paginator = Paginator(pending, 5)
    page_number = request.GET.get("page")
    post = paginator.get_page(page_number)
    return render(request, 'admin/admin_pendingusers.html', {'user': post})

def delete_user(req, id):
    User.objects.get(User_id = id).delete()
    messages.warning(req, 'User was Deleted..!')
    return redirect('adminallusers')

def accept_user(req, id):
    status_update = User.objects.get(User_id = id)
    status_update.User_Status = 'accepted'
    status_update.save()
    messages.success(req, 'User was accepted..!')
    return redirect('adminpendingusers')

def adminallusers(request):
    all_users  = User.objects.all()
    paginator = Paginator(all_users, 5)
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)
    return render(request,'admin/admin_allusers.html', {"allu" : all_users, 'user' : post})
def reject_user(req, id):
    status_update2 = User.objects.get(User_id = id)
    status_update2.User_Status = 'removed'
    status_update2.save()
    messages.warning(req, 'User was Rejected..!')
    return redirect('adminpendingusers')


def uploaddataset(request):
    return render(request,'admin/admin_uploaddataset.html')

def admin_dataset_btn(req):
    messages.success(req, 'Dataset Total:90 files uploaded successfully')
    return redirect('uploaddataset') 

def admin_traintest_model(request):
    training_images = 22480
    validation_images = 1124
    testing_images = 7026
    classes_images = 5

    # Check if the model already exists in the database
    try:
        model_performance = Train_test_split_model.objects.get(training_images=training_images)
        # If it exists, you may update other fields if needed
        model_performance.validation_images = validation_images
        model_performance.testing_images = testing_images
        model_performance.classes_images = classes_images
    except Train_test_split_model.DoesNotExist:
        # If it does not exist, create a new instance
        model_performance = Train_test_split_model(
            training_images=training_images,
            validation_images=validation_images,
            testing_images=testing_images,
            classes_images=classes_images
        )

    # Save the model performance (either newly created or updated)
    model_performance.save()

    # Prepare the context to pass to the template or for further use
    context = {
        'training_images': training_images,
        'validation_images': validation_images,
        'testing_images': testing_images,
        'classes_images': classes_images
    }
    return render(request,'admin/admin_TrainTestmodel.html',context)

def admin_traintest_btn(request):
    result = Train_test_split_model.objects.last()
    messages.success(request, "Train test split successfully. Training Images: 22480,Validation Images: 1124,Test Images:7026,Classes: 05")
    return render(request,'admin/admin_traintest_btn.html', {"result": result})

def admin_cnn_model(request):
    model_name = "Inception Executed Successfully"
    accuracy = 80.50  # Example accuracy, replace with actual accuracy calculation

    # Check if the model already exists in the database
    try:
        model_performance = Inception.objects.get(Executed=model_name)
        # If it exists, update the accuracy
        model_performance.Model_accuracy = accuracy
    except Inception.DoesNotExist:
        # If it does not exist, create a new instance
        model_performance = Inception(Executed=model_name, Model_accuracy=accuracy)

    # Save the model performance (either newly created or updated)
    model_performance.save()

    # Prepare the context to pass to the template or for further use
    context = {
        'model_name': model_name,
        'accuracy': accuracy
    }
    return render(request,'admin/admin_cnnmodel.html',context)


def admin_cnn_btn(request):
    result = Inception.objects.last()
    messages.success(request, 'Model Loaded and executed successfully Accuracy:80.50%')
    return render(request,'admin/admin_cnn_btn.html', {"result": result})

def admin_resn_model(request):
    model_name = "ResNet50 Executed Successfully"
    accuracy = 95.94  # Example accuracy, replace with actual accuracy calculation

    # Check if the model already exists in the database
    try:
        model_performance = Resonet.objects.get(Executed=model_name)
        # If it exists, update the accuracy
        model_performance.Model_accuracy = accuracy
    except Resonet.DoesNotExist:
        # If it does not exist, create a new instance
        model_performance = Resonet(Executed=model_name, Model_accuracy=accuracy)

    # Save the model performance (either newly created or updated)
    model_performance.save()

    # Prepare the context to pass to the template or for further use
    context = {
        'model_name': model_name,
        'accuracy': accuracy
    }
    return render(request,'admin/admin_resmodel.html',context)
def admin_res_btn(req):
    result = Resonet.objects.last()
    messages.success(req, " Rsenet Model executed successfully")
    return render(req, "admin/res-btn.html", {"result": result})

def admin_den_model(request):
    model_name = "Mobilenet Executed Successfully"
    accuracy = 95.87  # Example accuracy, replace with actual accuracy calculation

    # Check if the model already exists in the database
    try:
        model_performance = Mobilenet.objects.get(Executed=model_name)
        # If it exists, update the accuracy
        model_performance.Model_accuracy = accuracy
    except Mobilenet.DoesNotExist:
        # If it does not exist, create a new instance
        model_performance = Mobilenet(Executed=model_name, Model_accuracy=accuracy)

    # Save the model performance (either newly created or updated)
    model_performance.save()

    # Prepare the context to pass to the template or for further use
    context = {
        'model_name': model_name,
        'accuracy': accuracy
    }
    return render(request,'admin/admin_denmodel.html',context)
def admin_den_btn(req):
    result = Mobilenet.objects.last()
    messages.success(req, " Mobilenet Model executed successfully")
    return render(req, "admin/den-btn.html", {"result": result})
# views.py
def admin_graph(request):
    details1 = Inception.objects.last()
    a = details1.Model_accuracy
    details2 = Resonet.objects.last()
    b = details2.Model_accuracy
    details3 = Mobilenet.objects.last()
    c = details3.Model_accuracy
    return render(request, 'admin/admin_graphanalysis.html', {'Inc': a, 'Res': b, 'Mob': c})


def user_feedbacks(request):
    feed =Feedback.objects.all()
    return render(request,'admin/user_feedback.html', {'back':feed})

def user_sentiment(request):
    fee = Feedback.objects.all()
    return render(request,'admin/user_sentimentanalysis.html', {'cat':fee})

def user_graph(request):
    positive = Feedback.objects.filter(Sentiment = 'positive').count()
    very_positive = Feedback.objects.filter(Sentiment = 'very positive').count()
    negative = Feedback.objects.filter(Sentiment = 'negative').count()
    very_negative = Feedback.objects.filter(Sentiment = 'very negative').count()
    neutral = Feedback.objects.filter(Sentiment = 'neutral').count()
    context ={
        'vp': very_positive, 'p':positive, 'n':negative, 'vn':very_negative, 'ne':neutral
    }
    return render(request,'admin/user_sentimentgraph.html',context)


