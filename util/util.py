def calculate_discomfort(humidity, temperature):
    return 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3