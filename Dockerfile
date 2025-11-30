# Python 3.9 versiyasini asos qilib olamiz
FROM python:3.9-slim

# Ishchi papkani belgilaymiz
WORKDIR /app

# Kutubxonalarni o'rnatish uchun requirements.txt ni ko'chiramiz
COPY requirements.txt .

# Kutubxonalarni o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha kodini to'liq ko'chiramiz
COPY . .

# Botni ishga tushiramiz
CMD ["python", "main.py"]
