# Deep Learning with PyTorch - Vocabulary

## 📑 Table of Contents

- [Part 1: Fundamentals](#part-1-fundamentals)
  - [Chapter 1: Introduction](#chapter-1-introduction)
  - [Chapter 2: PyTorch Basics](#chapter-2-pytorch-basics)
  - [Chapter 3: Gradients](#chapter-3-gradients)
- [Part 2: Deep Learning](#part-2-deep-learning)
  - [Chapter 4: Neural Networks](#chapter-4-neural-networks)
  - [Chapter 5: Training](#chapter-5-training)

---

## Part 1: Fundamentals

### Chapter 1: Introduction

- **tensor** /ˈten.sər/ - a multi-dimensional array
  آرایه چندبعدی – پایه داده‌ها در PyTorch

- **scalar** /ˈskeɪ.lər/ - a single number
  عدد مفرد – تانسور با بعد صفر

- **vector** /ˈvek.tər/ - 1D tensor
  تانسور یک‌بعدی – لیستی از اعداد

### Chapter 2: PyTorch Basics

- **gradient** /ˈɡreɪ.di.ənt/ - derivative of function
  مشتق تابع – میزان تغییر خروجی نسبت به ورودی

- **parameter** /pəˈræm.ɪ.tər/ - trainable variable
  متغیر قابل آموزش – مقداری که مدل یاد می‌گیرد

### Chapter 3: Gradients

- **backpropagation** /ˌbæk.prɒp.əˈɡeɪ.ʃən/ - algorithm for computing gradients
  الگوریتم محاسبه گرادیان – قلب یادگیری عمیق

- **optimizer** /ˈɒp.tɪ.maɪ.zər/ - algorithm that updates parameters
  الگوریتم به‌روزرسانی پارامترها – مثل SGD یا Adam

---

## Part 2: Deep Learning

### Chapter 4: Neural Networks

- **neuron** /ˈnjʊə.rɒn/ - basic unit of neural network
  نورون – واحد پایه شبکه عصبی

- **layer** /ˈleɪ.ər/ - collection of neurons
  لایه – مجموعه‌ای از نورون‌ها

- **activation function** /ˌæk.tɪˈveɪ.ʃən ˈfʌŋk.ʃən/ - non-linear transformation
  تابع فعال‌سازی – تبدیل غیرخطی برای معرفی پیچیدگی

### Chapter 5: Training

- **epoch** /ˈiː.pɒk/ - one complete pass through training data
  دوره – یک بار کامل دیدن کل داده‌های آموزش

- **batch** /bætʃ/ - subset of training data
  دسته – زیرمجموعه‌ای از داده‌ها که با هم پردازش می‌شوند

- **loss function** /lɒs ˈfʌŋk.ʃən/ - measures model error
  تابع ضرر – خطای مدل را اندازه می‌گیرد