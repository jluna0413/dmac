import 'dart:convert';
import 'package:dmac_app/src/models/webarena_models.dart';
import 'package:dmac_app/src/services/api_service.dart';

/// Service for interacting with the WebArena API
class WebArenaService {
  final ApiService _apiService;

  WebArenaService(this._apiService);

  /// Get available WebArena tasks
  Future<List<WebArenaTask>> getTasks() async {
    final response = await _apiService.get('/api/webarena/tasks');

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['tasks'];
      return data.map((task) => WebArenaTask.fromJson(task)).toList();
    } else {
      throw Exception('Failed to load WebArena tasks');
    }
  }

  /// Get available WebArena models
  Future<List<WebArenaModel>> getModels() async {
    final response = await _apiService.get('/api/webarena/models');

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['models'];
      return data.map((model) => WebArenaModel.fromJson(model)).toList();
    } else {
      throw Exception('Failed to load WebArena models');
    }
  }

  /// Run a WebArena experiment
  Future<WebArenaRun> runExperiment({
    required String taskName,
    required String modelName,
    int numEpisodes = 1,
    int? timeout,
  }) async {
    final Map<String, dynamic> data = {
      'task_name': taskName,
      'model_name': modelName,
      'num_episodes': numEpisodes,
    };

    if (timeout != null) {
      data['timeout'] = timeout;
    }

    final response = await _apiService.post(
      '/api/webarena/runs',
      data: data,
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return WebArenaRun.fromJson(data['run_info']);
    } else {
      throw Exception('Failed to run WebArena experiment');
    }
  }

  /// Get WebArena runs
  Future<List<WebArenaRun>> getRuns({String? status}) async {
    final response = await _apiService.get(
      '/api/webarena/runs',
      queryParameters: status != null ? {'status': status} : null,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['runs'];
      return data.map((run) => WebArenaRun.fromJson(run)).toList();
    } else {
      throw Exception('Failed to load WebArena runs');
    }
  }

  /// Get a specific WebArena run
  Future<WebArenaRun> getRun(String runId) async {
    final response = await _apiService.get('/api/webarena/runs/$runId');

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return WebArenaRun.fromJson(data['run_info']);
    } else {
      throw Exception('Failed to load WebArena run');
    }
  }

  /// Stop a WebArena run
  Future<bool> stopRun(String runId) async {
    final response = await _apiService.delete('/api/webarena/runs/$runId');

    if (response.statusCode == 200) {
      return true;
    } else {
      throw Exception('Failed to stop WebArena run');
    }
  }

  /// Get results for a WebArena run
  Future<WebArenaResults> getRunResults(String runId) async {
    final response = await _apiService.get('/api/webarena/runs/$runId/results');

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return WebArenaResults.fromJson(data['results']);
    } else {
      throw Exception('Failed to load WebArena run results');
    }
  }

  /// Generate a visualization for WebArena results
  Future<String> generateVisualization({
    required String runId,
    required String visualizationType,
    Map<String, dynamic>? options,
  }) async {
    final Map<String, dynamic> data = {
      'run_id': runId,
      'visualization_type': visualizationType,
    };

    if (options != null) {
      data['options'] = options;
    }

    final response = await _apiService.post(
      '/api/webarena/visualizations',
      data: data,
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['visualization_url'];
    } else {
      throw Exception('Failed to generate WebArena visualization');
    }
  }
}
