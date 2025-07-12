from django.shortcuts import render,redirect
from django.http import HttpResponse,FileResponse
from PyPDF2 import PdfMerger,PdfReader,PdfWriter 
from django.contrib import messages
import io
from reportlab.pdfgen import canvas
from reportlab.lib.colors import toColor, Color
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User

from reportlab.lib.pagesizes import A4


def home(request):
    return render(request,"pdf/home.html")

def merger(request):
    
    if request.method=="POST":
        files=request.FILES.getlist("pdfs")
        merger=PdfMerger()

        for f in files:
            merger.append(f)
        buffer=io.BytesIO()
        merger.write(buffer)
        buffer.seek(0)

        return FileResponse(buffer,as_attachment=False,filename="merged.pdf",content_type="application/pdf")
        
    return render(request,"pdf/merger.html")

def split(request):
    if request.method=="POST":
        files=request.FILES["pdf"]
        start=int(request.POST.get("start"))
        end=int(request.POST.get("end"))

        reader=PdfReader(files)
        writer=PdfWriter()
        total_pages = len(reader.pages)

        if start < 1 or end > total_pages or start > end:
            messages.warning(request,"Pages should be in range og given PDF")
            return render(request,"pdf/split.html")

       
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])

        buffer=io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        return FileResponse(buffer,as_attachment=False,filename="split.pdf",content_type="application/pdf")


    return render(request,"pdf/split.html")

def create_custom_watermark(text, width, height, font_size, color, opacity):
    """Create a watermark PDF page with given size, color, and opacity."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))

    try:
        rgb_color = toColor(color)  # accepts 'red' or '#FF0000'
    except:
        rgb_color = Color(0.5, 0.5, 0.5)  # fallback to gray

    r, g, b = rgb_color.red, rgb_color.green, rgb_color.blue
    c.setFillColor(Color(r, g, b, alpha=opacity))

    c.setFont("Helvetica-Bold", font_size)
    c.translate(width / 2, height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.save()
    buffer.seek(0)
    return buffer

def watermark(request):
    if request.method == "POST":
        uploaded_pdf = request.FILES.get("pdf")
        text = request.POST.get("text", "CONFIDENTIAL")
        size = int(request.POST.get("size") or 40)
        color = request.POST.get("color") or "#888888"
        opacity = float(request.POST.get("opacity") or 0.5)

        if not uploaded_pdf or not text:
            return HttpResponse("Missing PDF or text", status=400)

        reader = PdfReader(uploaded_pdf)
        writer = PdfWriter()

        for page in reader.pages:
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)

            watermark_pdf = PdfReader(create_custom_watermark(text, width, height, size, color, opacity))
            watermark_page = watermark_pdf.pages[0]

            page.merge_page(watermark_page)
            writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        return FileResponse(output, content_type="application/pdf", filename="custom_watermarked.pdf")

    return render(request, "pdf/watermark.html")

def compress(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("pdf")
        if not uploaded_file:
            return HttpResponse("No PDF uploaded", status=400)

        reader = PdfReader(uploaded_file)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Clear metadata (optional)
        writer.add_metadata({})

        # Write to buffer
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        return FileResponse(output, content_type="application/pdf", filename="compressed.pdf")

    return render(request, "pdf/compress.html")

def signup(request):
    if request.method=="POST":
        username=request.POST.get("username")
        firstname=request.POST.get("firstname")
        lastname=request.POST.get("lastname")
        email=request.POST.get("email")
        password=request.POST.get("password")
        conf_password=request.POST.get("pass2")


        if len(username)>10:
            messages.warning(request,"username must be under 10 characters")
            return redirect("home")
        
        if password != conf_password:
            messages.warning(request,"Password not match")
            return redirect("home")
        
        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already taken. Please choose another.")
            return redirect("home")


        myuser=User.objects.create_user(username,email,password)
        myuser.first_name=firstname
        myuser.last_name=lastname

        myuser.save()
        messages.success(request,"Your Account has been Succesfully Created")
        return redirect("home")



    else:
        return HttpResponse("Not Found")
    
def handlelogin(request):
    if request.method=="POST":
        loginuser=request.POST.get("username")
        loginpass=request.POST.get("password")

        user=authenticate(username=loginuser,password=loginpass)
        
        if user is not None:
            login(request,user)
            messages.success(request,"successfully Logged In")
            return redirect('home')
        
        else:
            messages.warning(request,"Invalid Credentials")
            return redirect('home')
        
    else:
        return HttpResponse("Chal bhag")



def handlelogout(request):
    
        logout(request)
        messages.success(request,"Logout Succesfully")
        return redirect('home')
