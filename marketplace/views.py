from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from .models import User
from django.contrib.auth.decorators import login_required
from .models import Job, Proposal, FreelancerProfile
from django.contrib import messages
from .forms import JobForm, ProposalForm
from datetime import timedelta
from django.utils import timezone

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


from django.http import JsonResponse

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST
#test
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import Profile

#chat test
from .models import Conversation, Message, Notification, Feedback

#chatbot 
from django.views.decorators.csrf import csrf_exempt
import json

def landing_page(request):
    return render(request, 'marketplace/landing_page.html')

def home(request):
    return render(request, 'marketplace/home.html')

def recruiter_auth(request):
    return render(request, 'marketplace/recruiter.html')

def freelancer_auth(request):
    return render(request, 'marketplace/freelancer.html')

def recruiter_signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        signup_errors = []

        if password != confirm_password:
            signup_errors.append("Passwords do not match.")

        if User.objects.filter(username=email).exists():
            signup_errors.append("An account with this email already exists.")

        if signup_errors:
            return render(
                request,
                "marketplace/recruiter.html",
                {"signup_errors": signup_errors},
            )

        # create client user (recruiter)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name,
            role="client",
        )

        # Email on successful registration
        if user.email:
            send_mail(
        subject="Welcome to SkillConnect – Your Recruiter Account is Ready 🎉",
        message=(
            f"Hi {user.first_name or 'Recruiter'},\n\n"
            "Welcome to SkillConnect! 🎊\n\n"
            "Your recruiter account has been successfully created. You’re now ready to "
            "discover top freelancers and manage your hiring process with ease.\n\n"
            "🚀 What you can do next:\n"
            "• Post job openings and attract skilled freelancers\n"
            "• Review proposals and compare candidates\n"
            "• Chat directly with freelancers after acceptance\n"
            "• Track hiring progress from your recruiter dashboard\n\n"
            "🔐 Account Details:\n"
            f"• Registered Email: {user.email}\n"
            "• Account Type: Recruiter\n\n"
            "If you have any questions or need assistance, our support team is always here to help.\n\n"
            "We’re excited to help you build your dream team!\n\n"
            "Best regards,\n"
            "Team SkillConnect\n"
            "Connecting Talent with Opportunity."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )

        messages.success(request, "Recruiter registered successfully")
        return redirect("recruiter_auth")  # loads recruiter.html

    # GET fallback
    return render(request, "marketplace/recruiter.html")




def recruiter_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user and user.role == "client":
            login(request, user)

            # Email on successful login
            if user.email:
                send_mail(
        subject="New Login Alert – SkillConnect Recruiter Account 🔐",
        message=(
            f"Hi {user.first_name or 'Recruiter'},\n\n"
            "We detected a new login to your SkillConnect recruiter account.\n\n"
            "📍 Login details:\n"
            f"• Account Email: {user.email}\n"
            "• Time: Just now\n"
            "• Access Type: Recruiter Dashboard\n\n"
            "If this login was initiated by you, no action is required.\n\n"
            "🚨 If you do NOT recognize this activity:\n"
            "• Change your password immediately\n"
            "• Review your posted jobs and messages\n"
            "• Contact SkillConnect support if necessary\n\n"
            "Keeping your hiring workspace secure is our priority.\n\n"
            "Warm regards,\n"
            "Team SkillConnect\n"
            "Connecting Talent with Opportunity — Securely."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )

            return redirect("recruiter_dashboard")

        messages.error(request, "Invalid credentials")

    # render the combined recruiter page
    return render(request, "marketplace/recruiter.html")


def freelancer_signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        signup_errors = []

        if password != confirm_password:
            signup_errors.append("Passwords do not match.")

        if User.objects.filter(username=email).exists():
            signup_errors.append("An account with this email already exists.")

        if signup_errors:
            return render(
                request,
                "marketplace/freelancer.html",
                {"signup_errors": signup_errors},
            )

        # create freelancer user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name,
            role="freelancer",
        )

        # Email on successful registration
        if user.email:
            send_mail(
        subject="Welcome to SkillConnect – Your Freelance Journey Starts Here 🚀",
        message=(
            f"Hi {user.first_name or 'Freelancer'},\n\n"
            "Welcome to SkillConnect! 🎉\n\n"
            "Your freelancer account has been successfully created.\n\n"
            "With SkillConnect, you can:\n"
            "• Browse and apply for freelance jobs\n"
            "• Submit proposals to recruiters\n"
            "• Chat with recruiters after proposal acceptance\n"
            "• Build a strong professional profile\n\n"
            "👉 Next steps:\n"
            "1. Complete your profile\n"
            "2. Upload your resume\n"
            "3. Start applying for jobs\n\n"
            "We’re excited to have you on board and wish you great success!\n\n"
            "Best regards,\n"
            "Team SkillConnect\n"
            "Connecting Talent with Opportunity"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )

        messages.success(request, "Freelancer registered successfully")
        return redirect("freelancer_auth")

    return render(request, "marketplace/freelancer.html")



def freelancer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user and user.role == "freelancer":
            login(request, user)

            # Email on successful login
            if user.email:
                send_mail(
        subject="New Login Detected on Your SkillConnect Account 🔐",
        message=(
            f"Hi {user.first_name or 'Freelancer'},\n\n"
            "We noticed a new login to your SkillConnect account.\n\n"
            "📍 Login details:\n"
            f"• Account: {user.email}\n"
            "• Time: Just now\n"
            "• Platform: Web Browser\n\n"
            "If this was you, no further action is required.\n\n"
            "🚨 If you did NOT recognize this login:\n"
            "• Please change your password immediately\n"
            "• Review your recent activity\n"
            "• Contact our support team if needed\n\n"
            "Your security is important to us.\n\n"
            "Best regards,\n"
            "Team SkillConnect\n"
            "Secure. Reliable. Built for Professionals."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )

            return redirect("freelancer_dashboard")

        messages.error(request, "Invalid credentials")

    return render(request, "marketplace/freelancer.html")







@login_required
def recruiter_dashboard(request):
    # base querysets (no slicing)
    jobs_qs = Job.objects.filter(client=request.user).order_by('-created_at')
    proposals_qs = Proposal.objects.filter(job__client=request.user).order_by('-created_at')

    conversations = Conversation.objects.filter(recruiter=request.user).select_related("freelancer", "job")
    notifications_count = Notification.objects.filter(user=request.user,is_read=False).count()
    unread_chats = Message.objects.filter(conversation__recruiter=request.user).exclude(sender=request.user).filter(is_read=False).count()



    context = {
        "active_jobs": Job.objects.filter(client=request.user, status="open").count(),
        "total_proposals": proposals_qs.count(),
        "hired_freelancers": proposals_qs.filter(status="accepted").count(),
        "jobs_this_week": jobs_qs.count(),          # you can later add date filter
        "unread_proposals": proposals_qs.filter(status="pending").count(),
        "hires_this_month": proposals_qs.filter(status="accepted").count(),
        "pending_verifications": 0,                 # if you add this later
        "recent_jobs": jobs_qs[:20],                 # slicing is OK here (originally 5)
        "recent_proposals": proposals_qs[:10],       # and here (originally 6)
        "conversations": conversations,
        "notifications_count": notifications_count,  #notification testing
        "unread_chats": unread_chats,      #notification testing
    }

    return render(request, "marketplace/recruiter_dashboard.html", context)







@login_required
def freelancer_dashboard(request):
    user = request.user

    proposals_qs = Proposal.objects.filter(
        freelancer=user
    ).order_by('-created_at')

    jobs_won_qs = proposals_qs.filter(status="accepted")
    active_contracts = jobs_won_qs.filter(job__status="in_progress")

    recent_proposals = proposals_qs[:8]
    recommended_jobs = Job.objects.filter(status="open").order_by("-created_at")[:6]
    notifications_count = Notification.objects.filter(user=request.user,is_read=False).count()
    unread_chats = Message.objects.filter(conversation__freelancer=request.user).exclude(sender=request.user).filter(is_read=False).count()


    # ✅ FETCH CONVERSATIONS
    conversations = Conversation.objects.filter(
        freelancer=request.user
    ).select_related("recruiter", "job")

    # Primary skill
    primary_skill = ""
    try:
        profile = FreelancerProfile.objects.get(user=user)
        primary_skill = ", ".join([s.name for s in profile.skills.all()]) or ""
    except FreelancerProfile.DoesNotExist:
        pass

    total_proposals = proposals_qs.count()

    context = {
        "user": user,
        "primary_skill": primary_skill or "Freelancer",

        # Stats
        "active_proposals": proposals_qs.filter(status="pending").count(),
        "open_jobs_near_skill": recommended_jobs.count(),
        "total_proposals": total_proposals,
        "proposals_this_week": proposals_qs.count(),
        "jobs_won": jobs_won_qs.count(),
        "success_rate": round((jobs_won_qs.count() / max(1, total_proposals)) * 100, 1),
        "active_contracts": active_contracts.count(),
        "contracts_ending_soon": 0,
        "estimated_earnings": 0,

        # Display data
        "recommended_jobs": recommended_jobs,
        "recent_proposals": recent_proposals,

        # ✅ VERY IMPORTANT
        "conversations": conversations,
        "notifications_count": notifications_count,  #notification testing
        "unread_chats": unread_chats,
    }

    return render(request, "marketplace/freelancer_dashboard.html", context)




@login_required
def job_create(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.client = request.user
            job.save()

            # ✅ SUCCESS MESSAGE
            messages.success(request, "🎉 Job posted successfully!")

            return redirect("job_list")
    else:
        form = JobForm()

    return render(request, "marketplace/job_create.html", {"form": form})




@login_required
def job_list(request):
    user = request.user

    if getattr(user, "role", None) == "client":
        # Recruiter: show only their jobs
        jobs = Job.objects.filter(client=user).order_by("-created_at")
    else:
        # Freelancer: show all open jobs
        jobs = Job.objects.filter(status="open").order_by("-created_at")

    return render(request, "marketplace/job_list.html", {"jobs": jobs})









@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)

    proposal_form = None
    # Only freelancers can apply
    if getattr(request.user, "role", None) == "freelancer" and request.user != job.client:
        if request.method == "POST":
            form = ProposalForm(request.POST)
            if form.is_valid():
                proposal = form.save(commit=False)
                proposal.job = job
                proposal.freelancer = request.user
                proposal.save()
                messages.success(request, "Your proposal has been submitted! 🎉")
                return redirect("job_detail", pk=job.pk)
            else:
                proposal_form = form
        else:
            proposal_form = ProposalForm()
    # Recruiter or others
    context = {
        "job": job,
        "proposal_form": proposal_form,
    }
    return render(request, "marketplace/job_detail.html", context)




@login_required
def proposal_create(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

    # ---------------------------------------
    # 1️⃣ ROLE & PERMISSION CHECK
    # ---------------------------------------
    if getattr(request.user, "role", None) != "freelancer" or request.user == job.client:
        messages.error(request, "You are not allowed to submit a proposal for this job.")
        return redirect("job_detail", pk=job.pk)

    # ---------------------------------------
    # 2️⃣ JOB STATUS CHECK
    # ---------------------------------------
    if job.status != "open":
        messages.error(request, "This job is not accepting new proposals.")
        return redirect("job_detail", pk=job.pk)

    # ---------------------------------------
    # 3️⃣ PROFILE + RESUME CHECK (IMPORTANT)
    # ---------------------------------------
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if not profile.resume:
        messages.error(
            request,
            "You must upload your resume before applying for a job."
        )
        return redirect("freelancer_profile", pk=request.user.pk)

    # ---------------------------------------
    # 4️⃣ PREVENT DUPLICATE APPLICATION
    # ---------------------------------------
    if Proposal.objects.filter(job=job, freelancer=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect("job_detail", pk=job.pk)

    # ---------------------------------------
    # 5️⃣ HANDLE FORM SUBMISSION
    # ---------------------------------------
    if request.method == "POST":
        form = ProposalForm(request.POST)

        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.job = job
            proposal.freelancer = request.user
            proposal.status = "pending"
            proposal.save()

            # 🔔 Notify recruiter about new proposal
            Notification.objects.create(user=job.client,text=f"New proposal received for '{job.title}' from {request.user.first_name or 'a freelancer'}")


            # ---------------------------------------
            # 6️⃣ CREATE / GET CHAT CONVERSATION
            # ---------------------------------------
            Conversation.objects.get_or_create(
                job=job,
                recruiter=job.client,
                freelancer=request.user
            )

            # Email to freelancer
            if request.user.email:
                send_mail(
        subject="Your Application Has Been Submitted Successfully 🚀",
        message=(
            f"Hi {request.user.first_name or 'Freelancer'},\n\n"
            "Thank you for applying through SkillConnect!\n\n"
            "✅ Your application for the selected job role has been successfully submitted and is now under review by the recruiter.\n\n"
            "🔍 What happens next?\n"
            "• The recruiter will review your proposal and profile\n"
            "• You may be shortlisted or contacted for further discussion\n"
            "• If accepted, you’ll be able to chat directly with the recruiter\n\n"
            "📌 Tip: Keep your profile updated and check your dashboard regularly for updates.\n\n"
            "We’ll notify you as soon as there’s any progress on your application.\n\n"
            "Best of luck!\n\n"
            "Warm regards,\n"
            "Team SkillConnect\n"
            "Connecting Talent with Opportunity"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=True,
    )

            messages.success(
                request,
                "Your proposal has been submitted successfully! 🎉"
            )
            return redirect("job_detail", pk=job.pk)

        # ---------------------------------------
        # 7️⃣ FORM ERRORS → RE-RENDER PAGE
        # ---------------------------------------
        return render(request, "marketplace/job_detail.html", {
            "job": job,
            "proposal_form": form,
        })

    # ---------------------------------------
    # 8️⃣ BLOCK DIRECT GET ACCESS
    # ---------------------------------------
    return redirect("job_detail", pk=job.pk)





@login_required
def proposal_accept(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    job = proposal.job
    

    # only job owner (recruiter) can accept
    if getattr(request.user, "role", None) != "client" or request.user != job.client:
        messages.error(request, "You are not allowed to modify this proposal.")
        return redirect("job_detail", pk=job.pk)

    if request.method == "POST":
        proposal.status = "accepted"
        proposal.save()

        # mark job as in progress
        if job.status == "open":
            job.status = "in_progress"
            job.save()

        # 🔔 Notify freelancer about job status change
        Notification.objects.create(user=proposal.freelancer, text=f"Job '{job.title}' is now in progress 🚀")

        # ✅ CREATE CHAT CONVERSATION
        Conversation.objects.get_or_create(
            recruiter=job.client,
            freelancer=proposal.freelancer,
            job=job
        )

        # ✅ send email to freelancer
        try:
            job_link = request.build_absolute_uri(
                reverse("job_detail", args=[job.pk])
            )

            subject = f"Your proposal was ACCEPTED for '{job.title}'"
            message = (
                f"Hi {proposal.freelancer.first_name or 'Freelancer'},\n\n"
                f"Good news! The client '{job.client.first_name}' has ACCEPTED "
                f"your proposal for the job:\n\n"
                f"    {job.title}\n\n"
                f"Bid amount: ₹{proposal.bid_amount}\n"
                f"Job link: {job_link}\n\n"
                f"You can now coordinate with the client via chat.\n\n"
                f"– SkillConnect"
            )
            Notification.objects.create(user=proposal.freelancer,text=f"Your proposal for '{job.title}' was accepted 🎉")

            

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[proposal.freelancer.email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, "Proposal accepted. Chat unlocked 💬")
        return redirect("job_detail", pk=job.pk)

    return redirect("job_detail", pk=job.pk)



@login_required
def proposal_reject(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    job = proposal.job

    # only job owner (recruiter) can reject
    if getattr(request.user, "role", None) != "client" or request.user != job.client:
        messages.error(request, "You are not allowed to modify this proposal.")
        return redirect("job_detail", pk=job.pk)

    if request.method == "POST":
        proposal.status = "rejected"
        proposal.save()

        # ✅ send email to freelancer
        try:
            job_link = request.build_absolute_uri(
                reverse("job_detail", args=[job.pk])
            )

            subject = f"Your proposal was REJECTED for '{job.title}'"
            message = (
                f"Hi {proposal.freelancer.first_name or 'Freelancer'},\n\n"
                f"The client '{job.client.first_name}' has REJECTED "
                f"your proposal for the job:\n\n"
                f"    {job.title}\n\n"
                f"Bid amount: ₹{proposal.bid_amount}\n"
                f"Job link: {job_link}\n\n"
                f"Don't be discouraged – you can keep applying to other jobs "
                f"on SkillConnect.\n\n"
                f"– SkillConnect"
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[proposal.freelancer.email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, "You have rejected this proposal ❌")
        return redirect("job_detail", pk=job.pk)

    return redirect("job_detail", pk=job.pk)







#landing page statics
def api_stats(request):
    return JsonResponse({
        "total_jobs": Job.objects.count(),
        "total_users": User.objects.count(),
        "total_proposals": Proposal.objects.count(),
        "active_now":  (User.objects.filter(is_active=True).count()),  # example
        "server_time": timezone.now().isoformat(),
    })



#recruiter profile
@login_required
def recruiter_profile(request, pk=None):
    recruiter = request.user  # logged-in recruiter

    # if pk is provided (public profile view)
    if pk:
        recruiter = get_object_or_404(User, pk=pk)

    # Fetch data for profile page
    posted_jobs = Job.objects.filter(client=recruiter).order_by("-created_at")
    recent_activity = []   # Fill with your activity model if you have one

    context = {
        "recruiter": recruiter,
        "posted_jobs": posted_jobs,
        "recent_activity": recent_activity,
    }
    return render(request, "marketplace/recruiter_profile.html", context)




@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)

    # Only owner (recruiter) can edit
    if request.user != job.client:
        messages.error(request, "You are not allowed to edit this job.")
        return redirect("job_detail", pk=job.pk)

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated.")
            return redirect("job_detail", pk=job.pk)
    else:
        form = JobForm(instance=job)

    return render(request, "marketplace/job_edit.html", {"form": form, "job": job})


@login_required
def recruiter_profile_edit(request, pk):
    recruiter = get_object_or_404(User, pk=pk)

    if request.user != recruiter:
        messages.error(request, "Not allowed")
        return redirect("recruiter_profile", pk=pk)

    # ✅ SAFE: creates profile if missing
    profile, created = Profile.objects.get_or_create(user=recruiter)

    if request.method == "POST":
        profile.bio = request.POST.get("bio", "")
        profile.company = request.POST.get("company", "")
        profile.city = request.POST.get("profile_city", "")

        image = request.FILES.get("profile_image")

        if image:
            # Image validation
            if image.size > 2 * 1024 * 1024:
                messages.error(request, "Image must be under 2MB")
                return redirect("recruiter_profile_edit", pk=pk)

            if not image.content_type.startswith("image/"):
                messages.error(request, "Invalid image type")
                return redirect("recruiter_profile_edit", pk=pk)

            profile.profile_image = image

        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect("recruiter_profile", pk=pk)

    return render(request, "recruiter/profile_edit.html", {
        "profile": profile
    })



#test

def validate_profile_image(image):
    # 1️⃣ File size (2 MB limit)
    max_size = 2 * 1024 * 1024  # 2 MB
    if image.size > max_size:
        raise ValidationError("Image size should be less than 2 MB.")

    # 2️⃣ File extension check
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
    ext = image.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Only JPG, JPEG, PNG, or WEBP images are allowed.")

    # 3️⃣ Ensure it is a real image
    try:
        get_image_dimensions(image)
    except Exception:
        raise ValidationError("Uploaded file is not a valid image.")
    


#freelancer profile test
def freelancer_profile(request, pk):
    freelancer = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=freelancer)

    # 🔹 Convert comma-separated strings to lists
    skills_list = []
    tech_stack_list = []

    if profile.skills:
        skills_list = [s.strip() for s in profile.skills.split(",")]

    if profile.tech_stack:
        tech_stack_list = [t.strip() for t in profile.tech_stack.split(",")]

    context = {
        "freelancer": freelancer,
        "skills_list": skills_list,
        "tech_stack_list": tech_stack_list,
    }

    return render(request, "marketplace/freelancer_profile.html", context)




#freelancer profile edit test
@login_required
def freelancer_profile_edit(request, pk):
    freelancer = get_object_or_404(User, pk=pk)

    if request.user != freelancer:
        messages.error(request, "Unauthorized access")
        return redirect("home")

    profile = freelancer.profile

    if request.method == "POST":
        profile.education = request.POST.get("education", "")
        profile.experience = request.POST.get("experience", "")
        profile.tech_stack = request.POST.get("tech_stack", "")
        profile.skills = request.POST.get("skills", "")
        profile.bio = request.POST.get("bio", "")
        profile.city = request.POST.get("city", "")

        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        if request.FILES.get("resume"):
            profile.resume = request.FILES["resume"]

        profile.save()

        messages.success(request, "Profile updated successfully")
        return redirect(reverse("freelancer_profile", args=[freelancer.pk]))

    return redirect("freelancer_profile", pk=pk)



@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # 🔒 Security
    if request.user not in [conversation.recruiter, conversation.freelancer]:
        return HttpResponseForbidden("Not allowed")

    messages_qs = conversation.messages.order_by("timestamp")
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)


    # ✅ mark received messages as read
    messages_qs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        uploaded_file = request.FILES.get("file")  # 🔥 THIS WAS MISSING

        if text or uploaded_file:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text,
                file=uploaded_file
            )


            # 🔔 Notify the other user
            receiver = (conversation.freelancer if request.user == conversation.recruiter else conversation.recruiter)
            Notification.objects.create(user=receiver, text=f"New message from {request.user.first_name or 'User'}")
        

        return redirect("chat_room", conversation_id=conversation.id)

    return render(request, "marketplace/chat_room.html", {
        "conversation": conversation,
        "messages": messages_qs
    })


#Notifications html page test
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    # Mark as read
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, "marketplace/notifications.html", {
        "notifications": notifications
    })


#chat.html view
@login_required
def chat_list(request):
    user = request.user

    if user.role == "client":  # recruiter
        conversations = Conversation.objects.filter(
            recruiter=user
        ).select_related("freelancer", "job")

    else:  # freelancer
        conversations = Conversation.objects.filter(
            freelancer=user
        ).select_related("recruiter", "job")

    return render(request, "marketplace/chat_list.html", {
        "conversations": conversations
    })


#feedback for skillconnect view 
@login_required
def feedback_create(request):
    if request.method == "POST":
        rating = request.POST.get("rating")
        category = request.POST.get("category")
        message = request.POST.get("message")

        if not rating or not category or not message:
            messages.error(request, "All fields are required.")
            return redirect("feedback")

        Feedback.objects.create(
            user=request.user,
            rating=int(rating),
            category=category,
            message=message,
        )

        # ✅ SUCCESS TOAST
        messages.success(request, "Thank you for your feedback! 💚")

        # 🔁 Redirect based on role
        if getattr(request.user, "role", "") == "freelancer":
            return redirect("freelancer_dashboard")
        else:
            return redirect("recruiter_dashboard")

    return render(request, "marketplace/feedback_form.html")



#chabot testing
@login_required
def chatbot_reply(request):
    # ✅ READ MESSAGE FROM QUERY PARAM
    message = request.GET.get("message", "").lower().strip()

    if not message:
        return JsonResponse({"reply": "❌ Please type something"})

    # ------------------
    # SMART BOT LOGIC
    # ------------------
    if message in ["hi"]:
        reply = "👋 Hi! How can I help you today?"

    elif "hello" in message:
        reply = "Hello."

    elif "hey" in message:
        reply = "tell me what can i do for you."

    elif "good morning" in message:
        reply = "Good Morning Sir."

    elif "good night" in message:
        reply = "Good Night sir."

    elif "doubt" in message:
        reply = "Tell me what doubts u have ill solve it." 

    elif "post" in message:
        reply = "You can post jobs from your Recruiter dashboard."  

    elif "search" in message:
        reply = "you can search jobs according to your skills."

    elif "skillconnect" in message:
        reply = "skillconnect is web based platform for recruiters & freelancers"                            

    elif "job" in message:
        reply = "📝 You can browse jobs or post a new job from your dashboard."

    elif "proposal" in message:
        reply = "📄 Proposals help freelancers apply for jobs. Recruiters can accept or reject them."

    elif "chat" in message:
        reply = "💬 You can chat after a proposal is accepted."

    elif "resume" in message:
        reply = "📎 You can upload your resume while applying for a job."

    elif "bye" in message:
        reply = "👋 Goodbye! Have a great day 😊"

    else:
        reply = "🤖 I didn’t understand that. Try asking about jobs, proposals, chat, or resume."

    return JsonResponse({"reply": reply})



#aboutus page 
def about_us(request):
    return render(request, "marketplace/aboutus.html")


#sidebar dashboard redirect

@login_required
def dashboard_redirect(request):
    user = request.user

    if getattr(user, "role", None) == "client":
        return redirect("recruiter_dashboard")

    elif getattr(user, "role", None) == "freelancer":
        return redirect("freelancer_dashboard")

    # fallback safety
    return redirect("job_list")

















