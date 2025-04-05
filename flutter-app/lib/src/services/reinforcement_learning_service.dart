import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

/// Service for interacting with reinforcement learning systems
class ReinforcementLearningService {
  final String _openManusRLEndpoint;
  final String _deepSeekRLEndpoint;
  
  /// Constructor
  ReinforcementLearningService({
    String? openManusRLEndpoint,
    String? deepSeekRLEndpoint,
  }) : 
    _openManusRLEndpoint = openManusRLEndpoint ?? 'http://localhost:8000/api/openmanus-rl',
    _deepSeekRLEndpoint = deepSeekRLEndpoint ?? 'http://localhost:8001/api/deepseek-rl';
  
  /// Submit feedback to OpenManus-RL
  Future<bool> submitOpenManusRLFeedback({
    required String agentId,
    required String sessionId,
    required Map<String, dynamic> data,
    required double reward,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_openManusRLEndpoint/feedback'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'agent_id': agentId,
          'session_id': sessionId,
          'data': data,
          'reward': reward,
        }),
      );
      
      if (response.statusCode == 200) {
        return true;
      } else {
        debugPrint('Failed to submit OpenManus-RL feedback: ${response.body}');
        return false;
      }
    } catch (e) {
      debugPrint('Error submitting OpenManus-RL feedback: $e');
      return false;
    }
  }
  
  /// Submit feedback to DeepSeek-RL
  Future<bool> submitDeepSeekRLFeedback({
    required String agentId,
    required String sessionId,
    required Map<String, dynamic> data,
    required double reward,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_deepSeekRLEndpoint/feedback'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'agent_id': agentId,
          'session_id': sessionId,
          'data': data,
          'reward': reward,
        }),
      );
      
      if (response.statusCode == 200) {
        return true;
      } else {
        debugPrint('Failed to submit DeepSeek-RL feedback: ${response.body}');
        return false;
      }
    } catch (e) {
      debugPrint('Error submitting DeepSeek-RL feedback: $e');
      return false;
    }
  }
  
  /// Get OpenManus-RL training status
  Future<Map<String, dynamic>> getOpenManusRLStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$_openManusRLEndpoint/status'),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to get OpenManus-RL status: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to get status',
        };
      }
    } catch (e) {
      debugPrint('Error getting OpenManus-RL status: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
  
  /// Get DeepSeek-RL training status
  Future<Map<String, dynamic>> getDeepSeekRLStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$_deepSeekRLEndpoint/status'),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to get DeepSeek-RL status: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to get status',
        };
      }
    } catch (e) {
      debugPrint('Error getting DeepSeek-RL status: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
  
  /// Start OpenManus-RL training
  Future<bool> startOpenManusRLTraining({
    required String agentId,
    required Map<String, dynamic> config,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_openManusRLEndpoint/train'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'agent_id': agentId,
          'config': config,
        }),
      );
      
      if (response.statusCode == 200) {
        return true;
      } else {
        debugPrint('Failed to start OpenManus-RL training: ${response.body}');
        return false;
      }
    } catch (e) {
      debugPrint('Error starting OpenManus-RL training: $e');
      return false;
    }
  }
  
  /// Start DeepSeek-RL training
  Future<bool> startDeepSeekRLTraining({
    required String agentId,
    required Map<String, dynamic> config,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_deepSeekRLEndpoint/train'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'agent_id': agentId,
          'config': config,
        }),
      );
      
      if (response.statusCode == 200) {
        return true;
      } else {
        debugPrint('Failed to start DeepSeek-RL training: ${response.body}');
        return false;
      }
    } catch (e) {
      debugPrint('Error starting DeepSeek-RL training: $e');
      return false;
    }
  }
  
  /// Get OpenManus-RL model performance
  Future<Map<String, dynamic>> getOpenManusRLPerformance({
    required String agentId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$_openManusRLEndpoint/performance/$agentId'),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to get OpenManus-RL performance: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to get performance',
        };
      }
    } catch (e) {
      debugPrint('Error getting OpenManus-RL performance: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
  
  /// Get DeepSeek-RL model performance
  Future<Map<String, dynamic>> getDeepSeekRLPerformance({
    required String agentId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$_deepSeekRLEndpoint/performance/$agentId'),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to get DeepSeek-RL performance: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to get performance',
        };
      }
    } catch (e) {
      debugPrint('Error getting DeepSeek-RL performance: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
}
