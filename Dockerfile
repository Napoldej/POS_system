# Step 1: Use an official Python image as the base image
FROM python:3-alpine


# Step 2: Set environment variables to avoid Python writing bytecode files and to ensure logging is printed to console
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Copy the requirements.txt file into the container
COPY requirements.txt .

# Step 5: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the entire project into the container
COPY . .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Step 7: Expose the port that Django will run on (e.g., 8000)
EXPOSE 8000

# Step 8: Set the entrypoint to run the application using Gunicorn
CMD [ "./entrypoint.sh"]

