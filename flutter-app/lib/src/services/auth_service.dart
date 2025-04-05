import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:dmac_app/src/models/user.dart';
import 'package:dmac_app/src/services/api_service.dart';
import 'package:dmac_app/src/services/storage_service.dart';

/// Service for handling authentication
class AuthService extends ChangeNotifier {
  final ApiService _apiService;
  final StorageService _storageService;
  
  User? _currentUser;
  String? _token;
  bool _isLoading = false;
  
  AuthService(this._apiService, this._storageService) {
    // Load token and user data from storage
    _loadFromStorage();
  }
  
  /// Get the current user
  User? get currentUser => _currentUser;
  
  /// Get the authentication token
  String? get token => _token;
  
  /// Check if the user is authenticated
  bool get isAuthenticated => _token != null && _currentUser != null;
  
  /// Check if authentication is in progress
  bool get isLoading => _isLoading;
  
  /// Load authentication data from storage
  Future<void> _loadFromStorage() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      // Load token
      _token = await _storageService.getSecureString(StorageService.keyToken);
      
      if (_token != null) {
        // Set token in API service
        _apiService.setToken(_token!);
        
        // Load user data
        final userData = _storageService.getObject(StorageService.keyUser);
        if (userData != null) {
          _currentUser = User.fromJson(userData);
        } else {
          // If we have a token but no user data, fetch the user profile
          await _fetchUserProfile();
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error loading authentication data: $e');
      }
      // Clear authentication data on error
      await logout();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Fetch the user profile from the API
  Future<void> _fetchUserProfile() async {
    try {
      final response = await _apiService.get('/api/auth/profile');
      
      if (response['success'] == true && response['user'] != null) {
        _currentUser = User.fromJson(response['user']);
        
        // Save user data to storage
        await _storageService.setObject(
          StorageService.keyUser,
          _currentUser!.toJson(),
        );
      } else {
        // If we couldn't fetch the user profile, clear authentication data
        await logout();
      }
    } catch (e) {
      // If we couldn't fetch the user profile, clear authentication data
      await logout();
      rethrow;
    }
  }
  
  /// Login with email and password
  Future<void> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await _apiService.post('/api/auth/login', data: {
        'email': email,
        'password': password,
      });
      
      if (response['success'] == true && response['token'] != null) {
        _token = response['token'];
        
        // Set token in API service
        _apiService.setToken(_token!);
        
        // Save token to secure storage
        await _storageService.setSecureString(
          StorageService.keyToken,
          _token!,
        );
        
        // Fetch user profile
        await _fetchUserProfile();
      } else {
        throw AuthException(
          response['error'] ?? 'Login failed',
        );
      }
    } catch (e) {
      if (e is ApiException) {
        throw AuthException(e.message);
      } else {
        throw AuthException('Login failed: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Register a new user
  Future<void> register(String name, String email, String password) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await _apiService.post('/api/auth/register', data: {
        'name': name,
        'email': email,
        'password': password,
      });
      
      if (response['success'] == true) {
        // After registration, login with the new credentials
        await login(email, password);
      } else {
        throw AuthException(
          response['error'] ?? 'Registration failed',
        );
      }
    } catch (e) {
      if (e is ApiException) {
        throw AuthException(e.message);
      } else {
        throw AuthException('Registration failed: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Logout the current user
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      // Clear token from API service
      _apiService.clearToken();
      
      // Clear authentication data from storage
      await _storageService.removeSecure(StorageService.keyToken);
      await _storageService.remove(StorageService.keyUser);
      
      // Clear current user and token
      _currentUser = null;
      _token = null;
    } catch (e) {
      if (kDebugMode) {
        print('Error during logout: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Update the user profile
  Future<void> updateProfile({
    String? name,
    String? email,
    String? avatarUrl,
  }) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final data = <String, dynamic>{};
      if (name != null) data['name'] = name;
      if (email != null) data['email'] = email;
      if (avatarUrl != null) data['avatar_url'] = avatarUrl;
      
      final response = await _apiService.put('/api/auth/profile', data: data);
      
      if (response['success'] == true && response['user'] != null) {
        _currentUser = User.fromJson(response['user']);
        
        // Save updated user data to storage
        await _storageService.setObject(
          StorageService.keyUser,
          _currentUser!.toJson(),
        );
      } else {
        throw AuthException(
          response['error'] ?? 'Failed to update profile',
        );
      }
    } catch (e) {
      if (e is ApiException) {
        throw AuthException(e.message);
      } else {
        throw AuthException('Failed to update profile: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Change the user's password
  Future<void> changePassword(
    String currentPassword,
    String newPassword,
  ) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await _apiService.put('/api/auth/password', data: {
        'current_password': currentPassword,
        'new_password': newPassword,
      });
      
      if (response['success'] != true) {
        throw AuthException(
          response['error'] ?? 'Failed to change password',
        );
      }
    } catch (e) {
      if (e is ApiException) {
        throw AuthException(e.message);
      } else {
        throw AuthException('Failed to change password: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Request a password reset
  Future<void> requestPasswordReset(String email) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await _apiService.post('/api/auth/reset-password', data: {
        'email': email,
      });
      
      if (response['success'] != true) {
        throw AuthException(
          response['error'] ?? 'Failed to request password reset',
        );
      }
    } catch (e) {
      if (e is ApiException) {
        throw AuthException(e.message);
      } else {
        throw AuthException('Failed to request password reset: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}

/// Exception for authentication errors
class AuthException implements Exception {
  final String message;
  
  AuthException(this.message);
  
  @override
  String toString() => 'AuthException: $message';
}
