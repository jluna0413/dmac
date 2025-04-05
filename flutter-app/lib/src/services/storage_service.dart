import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Service for handling local storage
class StorageService {
  late final SharedPreferences _prefs;
  late final FlutterSecureStorage _secureStorage;
  
  // Private constructor
  StorageService._({
    required SharedPreferences prefs,
    required FlutterSecureStorage secureStorage,
  })  : _prefs = prefs,
        _secureStorage = secureStorage;
  
  /// Initialize the storage service
  static Future<StorageService> init() async {
    final prefs = await SharedPreferences.getInstance();
    const secureStorage = FlutterSecureStorage();
    
    return StorageService._(
      prefs: prefs,
      secureStorage: secureStorage,
    );
  }
  
  // Regular storage methods (non-sensitive data)
  
  /// Save a string value
  Future<bool> setString(String key, String value) async {
    return await _prefs.setString(key, value);
  }
  
  /// Get a string value
  String? getString(String key) {
    return _prefs.getString(key);
  }
  
  /// Save a boolean value
  Future<bool> setBool(String key, bool value) async {
    return await _prefs.setBool(key, value);
  }
  
  /// Get a boolean value
  bool? getBool(String key) {
    return _prefs.getBool(key);
  }
  
  /// Save an integer value
  Future<bool> setInt(String key, int value) async {
    return await _prefs.setInt(key, value);
  }
  
  /// Get an integer value
  int? getInt(String key) {
    return _prefs.getInt(key);
  }
  
  /// Save a double value
  Future<bool> setDouble(String key, double value) async {
    return await _prefs.setDouble(key, value);
  }
  
  /// Get a double value
  double? getDouble(String key) {
    return _prefs.getDouble(key);
  }
  
  /// Save a list of strings
  Future<bool> setStringList(String key, List<String> value) async {
    return await _prefs.setStringList(key, value);
  }
  
  /// Get a list of strings
  List<String>? getStringList(String key) {
    return _prefs.getStringList(key);
  }
  
  /// Save an object as JSON
  Future<bool> setObject(String key, Map<String, dynamic> value) async {
    return await _prefs.setString(key, jsonEncode(value));
  }
  
  /// Get an object from JSON
  Map<String, dynamic>? getObject(String key) {
    final jsonString = _prefs.getString(key);
    if (jsonString == null) return null;
    
    try {
      return jsonDecode(jsonString) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }
  
  /// Remove a value
  Future<bool> remove(String key) async {
    return await _prefs.remove(key);
  }
  
  /// Clear all values
  Future<bool> clear() async {
    return await _prefs.clear();
  }
  
  // Secure storage methods (sensitive data)
  
  /// Save a secure string value
  Future<void> setSecureString(String key, String value) async {
    await _secureStorage.write(key: key, value: value);
  }
  
  /// Get a secure string value
  Future<String?> getSecureString(String key) async {
    return await _secureStorage.read(key: key);
  }
  
  /// Save a secure object as JSON
  Future<void> setSecureObject(String key, Map<String, dynamic> value) async {
    await _secureStorage.write(key: key, value: jsonEncode(value));
  }
  
  /// Get a secure object from JSON
  Future<Map<String, dynamic>?> getSecureObject(String key) async {
    final jsonString = await _secureStorage.read(key: key);
    if (jsonString == null) return null;
    
    try {
      return jsonDecode(jsonString) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }
  
  /// Remove a secure value
  Future<void> removeSecure(String key) async {
    await _secureStorage.delete(key: key);
  }
  
  /// Clear all secure values
  Future<void> clearSecure() async {
    await _secureStorage.deleteAll();
  }
  
  // Common storage keys
  static const String keyToken = 'auth_token';
  static const String keyUser = 'user_data';
  static const String keyThemeMode = 'theme_mode';
  static const String keyServerUrl = 'server_url';
  static const String keyDefaultModel = 'default_model';
  static const String keyOnboardingComplete = 'onboarding_complete';
}
