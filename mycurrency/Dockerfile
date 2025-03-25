# Use the official Python image from Docker Hub as the base image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /mycurrency

# Copy the requirements file into the container
COPY requirements.txt /mycurrency/

# Create a virtual environment
RUN python3 -m venv venv

# Set environment variables to use the virtual environment
ENV VIRTUAL_ENV /mycurrency/venv
ENV PATH /mycurrency/venv/bin:$PATH

RUN ./venv/bin/pip install --upgrade pip
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /mycurrency/

# Expose port 8000 to the outside world
EXPOSE 8000

ENV PATH="/mycurrency/venv/bin:$PATH"

# Set environment variables for superuser credentials
ENV DJANGO_SUPERUSER_USERNAME=
ENV DJANGO_SUPERUSER_EMAIL=
ENV DJANGO_SUPERUSER_PASSWORD=

# Command to create the superuser and start the server
# Command to apply migrations, create superuser, and start the server
CMD python manage.py migrate && \
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); \
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" && \
    python manage.py runserver 0.0.0.0:8000

