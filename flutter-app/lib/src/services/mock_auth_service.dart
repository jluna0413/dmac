import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dmac_app/src/models/user_model.dart';

/// A mock authentication service for development and testing
class MockAuthService extends ChangeNotifier {
  User? _currentUser;
  bool _isLoading = false;
  final List<User> _users = [];
  
  /// Get the current user
  User? get currentUser => _currentUser;
  
  /// Check if the authentication is in progress
  bool get isLoading => _isLoading;
  
  /// Get all users (for admin purposes)
  List<User> get users => List.unmodifiable(_users);
  
  /// Constructor
  MockAuthService() {
    _initializeUsers();
    _loadCurrentUser();
  }
  
  /// Initialize with default users
  void _initializeUsers() {
    // Admin user
    _users.add(User(
      id: '1',
      email: 'admin@dmac.ai',
      name: 'Admin User',
      role: UserRole.admin,
      avatarUrl: null,
    ));
    
    // Regular user
    _users.add(User(
      id: '2',
      email: 'user@dmac.ai',
      name: 'Test User',
      role: UserRole.user,
      avatarUrl: null,
    ));
    
    // Developer user
    _users.add(User(
      id: '3',
      email: 'dev@dmac.ai',
      name: 'Developer',
      role: UserRole.developer,
      avatarUrl: null,
    ));
    
    // Save the users to local storage
    _saveUsers();
  }
  
  /// Load the current user from local storage
  Future<void> _loadCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString('current_user');
    
    if (userJson != null) {
      try {
        final Map<String, dynamic> userData = json.decode(userJson);
        _currentUser = User.fromJson(userData);
        notifyListeners();
      } catch (e) {
        debugPrint('Error loading user: $e');
      }
    }
  }
  
  /// Save the current user to local storage
  Future<void> _saveCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    
    if (_currentUser != null) {
      final userJson = json.encode(_currentUser!.toJson());
      await prefs.setString('current_user', userJson);
    } else {
      await prefs.remove('current_user');
    }
  }
  
  /// Save all users to local storage
  Future<void> _saveUsers() async {
    final prefs = await SharedPreferences.getInstance();
    final usersJson = json.encode(_users.map((u) => u.toJson()).toList());
    await prefs.setString('users', usersJson);
  }
  
  /// Load all users from local storage
  Future<void> _loadUsers() async {
    final prefs = await SharedPreferences.getInstance();
    final usersJson = prefs.getString('users');
    
    if (usersJson != null) {
      try {
        final List<dynamic> usersData = json.decode(usersJson);
        _users.clear();
        _users.addAll(usersData.map((data) => User.fromJson(data)));
      } catch (e) {
        debugPrint('Error loading users: $e');
      }
    }
  }
  
  /// Login with email and password
  Future<User> login({required String email, required String password}) async {
    _isLoading = true;
    notifyListeners();
    
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));
    
    try {
      // Find the user by email
      final user = _users.firstWhere(
        (u) => u.email.toLowerCase() == email.toLowerCase(),
        orElse: () => throw Exception('User not found'),
      );
      
      // In a real app, you would check the password hash
      // For this mock service, we'll accept any password for the predefined users
      
      _currentUser = user;
      await _saveCurrentUser();
      
      return user;
    } catch (e) {
      throw Exception('Invalid email or password');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Login with OpenID
  Future<User> loginWithOpenID({required String provider}) async {
    _isLoading = true;
    notifyListeners();
    
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 2));
    
    try {
      // In a real app, this would redirect to the provider's auth page
      // For this mock service, we'll just return a random existing user
      final random = Random();
      final user = _users[random.nextInt(_users.length)];
      
      _currentUser = user;
      await _saveCurrentUser();
      
      return user;
    } catch (e) {
      throw Exception('OpenID authentication failed');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Auto-generate a login (for testing)
  Future<User> autoGenerateLogin() async {
    _isLoading = true;
    notifyListeners();
    
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));
    
    try {
      // Generate a random user
      final id = DateTime.now().millisecondsSinceEpoch.toString();
      final user = User(
        id: id,
        email: 'auto$id@dmac.ai',
        name: 'Auto User $id',
        role: UserRole.user,
        avatarUrl: null,
      );
      
      // Add to users list
      _users.add(user);
      await _saveUsers();
      
      // Set as current user
      _currentUser = user;
      await _saveCurrentUser();
      
      return user;
    } catch (e) {
      throw Exception('Failed to generate auto login');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Logout the current user
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();
    
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));
    
    _currentUser = null;
    await _saveCurrentUser();
    
    _isLoading = false;
    notifyListeners();
  }
  
  /// Create a new user (admin function)
  Future<User> createUser({
    required String email,
    required String name,
    required UserRole role,
  }) async {
    // Check if email already exists
    if (_users.any((u) => u.email.toLowerCase() == email.toLowerCase())) {
      throw Exception('Email already in use');
    }
    
    // Create new user
    final id = DateTime.now().millisecondsSinceEpoch.toString();
    final user = User(
      id: id,
      email: email,
      name: name,
      role: role,
      avatarUrl: null,
    );
    
    // Add to users list
    _users.add(user);
    await _saveUsers();
    
    notifyListeners();
    return user;
  }
  
  /// Update an existing user (admin function)
  Future<User> updateUser(User user) async {
    final index = _users.indexWhere((u) => u.id == user.id);
    
    if (index == -1) {
      throw Exception('User not found');
    }
    
    _users[index] = user;
    await _saveUsers();
    
    // If updating the current user, update that too
    if (_currentUser?.id == user.id) {
      _currentUser = user;
      await _saveCurrentUser();
    }
    
    notifyListeners();
    return user;
  }
  
  /// Delete a user (admin function)
  Future<void> deleteUser(String userId) async {
    final index = _users.indexWhere((u) => u.id == userId);
    
    if (index == -1) {
      throw Exception('User not found');
    }
    
    _users.removeAt(index);
    await _saveUsers();
    
    notifyListeners();
  }
}
