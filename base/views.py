from django.shortcuts import render
import google.generativeai as genai
import os
from django.contrib import messages
from django.conf import settings
# Create your views here.

genai.configure(api_key=settings.GEMINI_API_KEY)

def diet(request):

    if request.method == 'POST':
        # Process form data
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        exercise_level = request.POST.get('exercise_level')
        goal = request.POST.get('goal')
        diet_type = request.POST.get('diet_type')

        # Check for empty fields
        if not all([age, weight, height]):
            messages.error(request, "Please fill in all required fields * .")
            return render(request, 'base/diet.html', {'show_results': False})

        try:
            age = int(age)
            weight = float(weight)
            height = float(height)
        except ValueError:
            messages.error(request, "Please enter valid numbers for age, weight, and height.")
            return render(request, 'base/diet.html', {'show_results': False})

        # Calculate BMI
        bmi = weight / ((height / 100) ** 2)

        # Calculate maintenance calories (simplified formula)
        if gender == 'male':
            maintenance_calories = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            maintenance_calories = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # Adjust calories based on exercise level and goal
        if exercise_level == 'sedentary':
            maintenance_calories *= 1.2
        elif exercise_level == 'lightly_active':
            maintenance_calories *= 1.375
        elif exercise_level == 'moderately_active':
            maintenance_calories *= 1.55
        elif exercise_level == 'very_active':
            maintenance_calories *= 1.725
        elif exercise_level == 'extremely_active':
            maintenance_calories *= 1.9

        if goal == 'weight_loss':
            maintenance_calories -= 500
        elif goal == 'build_muscle':
            maintenance_calories += 300

        # Generate personalized diet plan using Gemini API
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""Generate a personalized Indian {diet_type} diet plan for a {age}-year-old {gender} with the following details:
    - Weight: {weight} kg
    - Height: {height} cm
    - BMI: {bmi:.1f}
    - Activity level: {exercise_level}
    - Daily calorie intake: {maintenance_calories:.0f} calories

    Don't use asterisks (*) anywhere in the answer

    Please provide a diet plan with 4 meals a day (breakfast, lunch, snack, and dinner) that meets the total daily calorie requirement of {maintenance_calories:.0f} calories. Include specific Indian dishes and portion sizes.

    Format the output as follows:
    Indian {diet_type} Diet Plan for a {age}-Year-Old {gender}
    Breakfast:
    • Item 1 (calories)
    • Item 2 (calories)
    Lunch:
    • Item 1 (calories)
    • Item 2 (calories)
    Snack:
    • Item 1 (calories)
    • Item 2 (calories)
    Dinner:
    • Item 1 (calories)
    • Item 2 (calories)
    
    IMP:

    • Point 1
    • Point 2
    • Point 3
    • Point 4
    • Point 5

    Use round bullet points (•) and make headings bold. Don't use asterisks."""

        response = model.generate_content(prompt)
        diet_plan = response.text

        context = {
            'show_results': True,
            'bmi': f"{bmi:.1f}",
            'maintenance_calories': f"{maintenance_calories:.0f}",
            'diet_plan': diet_plan,
        }
    else:
        context = {'show_results': False}

    return render(request, 'base/diet.html', context)