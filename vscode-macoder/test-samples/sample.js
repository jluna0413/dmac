/**
 * Sample JavaScript file for testing MaCoder VS Code Extension
 */

// A simple function to add two numbers
function add(a, b) {
    return a + b;
}

// A function to calculate factorial
function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// A class representing a person
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    greet() {
        return `Hello, my name is ${this.name} and I am ${this.age} years old.`;
    }

    // Calculate birth year based on current year and age
    getBirthYear() {
        const currentYear = new Date().getFullYear();
        return currentYear - this.age;
    }
}

// An async function to fetch data from an API
async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}

// A function with a callback
function processData(data, callback) {
    // Process the data
    const result = data.map(item => item * 2);
    
    // Call the callback with the result
    callback(result);
}

// A higher-order function
function createMultiplier(factor) {
    return function(number) {
        return number * factor;
    };
}

// Usage examples
const double = createMultiplier(2);
const triple = createMultiplier(3);

console.log(double(5)); // 10
console.log(triple(5)); // 15

// Export the functions and classes
module.exports = {
    add,
    factorial,
    Person,
    fetchData,
    processData,
    createMultiplier
};
