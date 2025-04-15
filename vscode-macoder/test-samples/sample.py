"""
Sample Python file for testing MaCoder VS Code Extension
"""

import math
import asyncio
import json
from typing import List, Dict, Any, Callable


# A simple function to add two numbers
def add(a: float, b: float) -> float:
    return a + b


# A function to calculate factorial
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)


# A class representing a person
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    def greet(self) -> str:
        return f"Hello, my name is {self.name} and I am {self.age} years old."
    
    # Calculate birth year based on current year and age
    def get_birth_year(self) -> int:
        from datetime import datetime
        current_year = datetime.now().year
        return current_year - self.age


# An async function to fetch data from an API
async def fetch_data(url: str) -> Dict[str, Any]:
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


# A function with a callback
def process_data(data: List[int], callback: Callable[[List[int]], None]) -> None:
    # Process the data
    result = [item * 2 for item in data]
    
    # Call the callback with the result
    callback(result)


# A higher-order function
def create_multiplier(factor: int) -> Callable[[int], int]:
    def multiplier(number: int) -> int:
        return number * factor
    return multiplier


# Usage examples
double = create_multiplier(2)
triple = create_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15


# Main function
def main():
    # Create a person
    person = Person("Alice", 30)
    print(person.greet())
    print(f"Birth year: {person.get_birth_year()}")
    
    # Calculate factorial
    print(f"Factorial of 5: {factorial(5)}")
    
    # Process some data
    data = [1, 2, 3, 4, 5]
    process_data(data, lambda result: print(f"Processed data: {result}"))


if __name__ == "__main__":
    main()
