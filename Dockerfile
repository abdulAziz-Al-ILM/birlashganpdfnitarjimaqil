# Python 3.9 slim versiyasini olamiz
FROM python:3.9-slim

# Tizim yangilanishi va OpenCV ishlashi uchun kerakli kutubxonalarni o'rnatamiz
# libgl1 va libglib2.0-0 aynan shu xatolikni tuzatadi
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Ishchi papkani belgilaymiz
WORKDIR /app

# Requirements faylini ko'chiramiz
COPY requirements.txt .

# Python kutubxonalarini o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha kodini ko'chiramiz
COPY . .

# Botni ishga tushiramiz
CMD ["python", "main.py"]
