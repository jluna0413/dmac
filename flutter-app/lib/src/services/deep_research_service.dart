import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

/// Service for interacting with Langchain and Open Deep Research
class DeepResearchService {
  final String _langchainEndpoint;
  final String _openDeepResearchEndpoint;
  
  /// Constructor
  DeepResearchService({
    String? langchainEndpoint,
    String? openDeepResearchEndpoint,
  }) : 
    _langchainEndpoint = langchainEndpoint ?? 'http://localhost:8002/api/langchain',
    _openDeepResearchEndpoint = openDeepResearchEndpoint ?? 'http://localhost:8003/api/deep-research';
  
  /// Run a Langchain query
  Future<Map<String, dynamic>> runLangchainQuery({
    required String query,
    required String chainType,
    Map<String, dynamic>? parameters,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_langchainEndpoint/query'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'query': query,
          'chain_type': chainType,
          'parameters': parameters ?? {},
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to run Langchain query: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to run query',
        };
      }
    } catch (e) {
      debugPrint('Error running Langchain query: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
  
  /// Get available Langchain chains
  Future<List<Map<String, dynamic>>> getLangchainChains() async {
    try {
      final response = await http.get(
        Uri.parse('$_langchainEndpoint/chains'),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['chains']);
      } else {
        debugPrint('Failed to get Langchain chains: ${response.body}');
        return [];
      }
    } catch (e) {
      debugPrint('Error getting Langchain chains: $e');
      return [];
    }
  }
  
  /// Run a deep research query
  Future<Map<String, dynamic>> runDeepResearch({
    required String query,
    required List<String> sources,
    int? maxResults,
    int? maxDepth,
    Map<String, dynamic>? options,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_openDeepResearchEndpoint/research'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'query': query,
          'sources': sources,
          'max_results': maxResults ?? 10,
          'max_depth': maxDepth ?? 3,
          'options': options ?? {},
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to run deep research: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to run research',
        };
      }
    } catch (e) {
      debugPrint('Error running deep research: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
  
  /// Get deep research sources
  Future<List<Map<String, dynamic>>> getDeepResearchSources() async {
    try {
      final response = await http.get(
        Uri.parse('$_openDeepResearchEndpoint/sources'),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['sources']);
      } else {
        debugPrint('Failed to get deep research sources: ${response.body}');
        return [];
      }
    } catch (e) {
      debugPrint('Error getting deep research sources: $e');
      return [];
    }
  }
  
  /// Get deep research status
  Future<Map<String, dynamic>> getDeepResearchStatus(String researchId) async {
    try {
      final response = await http.get(
        Uri.parse('$_openDeepResearchEndpoint/status/$researchId'),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to get deep research status: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to get status',
        };
      }
    } catch (e) {
      debugPrint('Error getting deep research status: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
  
  /// Get deep research results
  Future<Map<String, dynamic>> getDeepResearchResults(String researchId) async {
    try {
      final response = await http.get(
        Uri.parse('$_openDeepResearchEndpoint/results/$researchId'),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to get deep research results: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to get results',
        };
      }
    } catch (e) {
      debugPrint('Error getting deep research results: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
  
  /// Create a new Langchain chain
  Future<Map<String, dynamic>> createLangchainChain({
    required String name,
    required String description,
    required String chainType,
    required Map<String, dynamic> config,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_langchainEndpoint/chains'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'name': name,
          'description': description,
          'chain_type': chainType,
          'config': config,
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to create Langchain chain: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to create chain',
        };
      }
    } catch (e) {
      debugPrint('Error creating Langchain chain: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
  
  /// Add a new deep research source
  Future<Map<String, dynamic>> addDeepResearchSource({
    required String name,
    required String type,
    required String url,
    required Map<String, dynamic> config,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_openDeepResearchEndpoint/sources'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'name': name,
          'type': type,
          'url': url,
          'config': config,
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint('Failed to add deep research source: ${response.body}');
        return {
          'status': 'error',
          'message': 'Failed to add source',
        };
      }
    } catch (e) {
      debugPrint('Error adding deep research source: $e');
      return {
        'status': 'error',
        'message': e.toString(),
      };
    }
  }
}
