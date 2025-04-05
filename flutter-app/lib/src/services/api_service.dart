import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// Service for handling API requests to the DMac backend
class ApiService {
  late final Dio _dio;
  String? _baseUrl;
  String? _token;
  WebSocketChannel? _wsChannel;

  ApiService({String? baseUrl}) {
    _baseUrl = baseUrl ?? 'http://localhost:8080';
    _dio = Dio(
      BaseOptions(
        baseUrl: _baseUrl!,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add logging interceptor in debug mode
    if (kDebugMode) {
      _dio.interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
      ));
    }
  }

  /// Set the authentication token for API requests
  void setToken(String token) {
    _token = token;
    _dio.options.headers['Authorization'] = 'Bearer $_token';
  }

  /// Clear the authentication token
  void clearToken() {
    _token = null;
    _dio.options.headers.remove('Authorization');
  }

  /// Set the base URL for API requests
  void setBaseUrl(String baseUrl) {
    _baseUrl = baseUrl;
    _dio.options.baseUrl = baseUrl;
  }

  /// Get the current base URL
  String get baseUrl => _baseUrl ?? 'http://localhost:8080';

  /// Make a GET request to the API
  Future<dynamic> get(String path,
      {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
      );
      return response.data;
    } on DioException catch (e) {
      _handleError(e);
    }
  }

  /// Make a POST request to the API
  Future<dynamic> post(String path, {dynamic data}) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
      );
      return response.data;
    } on DioException catch (e) {
      _handleError(e);
    }
  }

  /// Make a PUT request to the API
  Future<dynamic> put(String path, {dynamic data}) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
      );
      return response.data;
    } on DioException catch (e) {
      _handleError(e);
    }
  }

  /// Make a DELETE request to the API
  Future<dynamic> delete(String path) async {
    try {
      final response = await _dio.delete(path);
      return response.data;
    } on DioException catch (e) {
      _handleError(e);
    }
  }

  /// Connect to a WebSocket for real-time communication
  WebSocketChannel connectWebSocket(String path) {
    final wsUrl = _baseUrl!.replaceFirst('http', 'ws') + path;
    _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));
    return _wsChannel!;
  }

  /// Close the WebSocket connection
  void closeWebSocket() {
    _wsChannel?.sink.close();
    _wsChannel = null;
  }

  /// Handle API errors
  void _handleError(DioException e) {
    if (e.response != null) {
      // The server responded with an error
      final statusCode = e.response!.statusCode;
      final data = e.response!.data;

      if (statusCode == 401) {
        throw UnauthorizedException(data['error'] ?? 'Unauthorized');
      } else if (statusCode == 403) {
        throw ForbiddenException(data['error'] ?? 'Forbidden');
      } else if (statusCode == 404) {
        throw NotFoundException(data['error'] ?? 'Not found');
      } else {
        throw ApiException(
          data['error'] ?? 'API error',
          statusCode: statusCode,
        );
      }
    } else {
      // Something happened in setting up or sending the request
      throw ApiException(
        e.message ?? 'Network error',
        statusCode: 0,
      );
    }
  }
}

/// Base exception for API errors
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, {this.statusCode});

  @override
  String toString() => 'ApiException: $message (Status code: $statusCode)';
}

/// Exception for 401 Unauthorized responses
class UnauthorizedException extends ApiException {
  UnauthorizedException(String message) : super(message, statusCode: 401);
}

/// Exception for 403 Forbidden responses
class ForbiddenException extends ApiException {
  ForbiddenException(String message) : super(message, statusCode: 403);
}

/// Exception for 404 Not Found responses
class NotFoundException extends ApiException {
  NotFoundException(String message) : super(message, statusCode: 404);
}
