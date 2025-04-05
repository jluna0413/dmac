/// Model class for WebArena tasks
class WebArenaTask {
  final String id;
  final String name;
  final String description;
  final String category;
  final Map<String, dynamic> metadata;
  
  WebArenaTask({
    required this.id,
    required this.name,
    required this.description,
    required this.category,
    required this.metadata,
  });
  
  factory WebArenaTask.fromJson(Map<String, dynamic> json) {
    return WebArenaTask(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      category: json['category'],
      metadata: json['metadata'] ?? {},
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'category': category,
      'metadata': metadata,
    };
  }
}

/// Model class for WebArena models
class WebArenaModel {
  final String id;
  final String name;
  final String description;
  final String provider;
  final Map<String, dynamic> metadata;
  
  WebArenaModel({
    required this.id,
    required this.name,
    required this.description,
    required this.provider,
    required this.metadata,
  });
  
  factory WebArenaModel.fromJson(Map<String, dynamic> json) {
    return WebArenaModel(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      provider: json['provider'],
      metadata: json['metadata'] ?? {},
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'provider': provider,
      'metadata': metadata,
    };
  }
}

/// Model class for WebArena runs
class WebArenaRun {
  final String id;
  final String taskName;
  final String modelName;
  final int numEpisodes;
  final int? timeout;
  final double startTime;
  final String status;
  final Map<String, dynamic>? results;
  
  WebArenaRun({
    required this.id,
    required this.taskName,
    required this.modelName,
    required this.numEpisodes,
    this.timeout,
    required this.startTime,
    required this.status,
    this.results,
  });
  
  factory WebArenaRun.fromJson(Map<String, dynamic> json) {
    return WebArenaRun(
      id: json['id'],
      taskName: json['task_name'],
      modelName: json['model_name'],
      numEpisodes: json['num_episodes'],
      timeout: json['timeout'],
      startTime: json['start_time'].toDouble(),
      status: json['status'],
      results: json['results'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'task_name': taskName,
      'model_name': modelName,
      'num_episodes': numEpisodes,
      'timeout': timeout,
      'start_time': startTime,
      'status': status,
      'results': results,
    };
  }
}

/// Model class for WebArena results
class WebArenaResults {
  final String runId;
  final bool success;
  final double successRate;
  final int totalSteps;
  final Map<String, int> actionCounts;
  final List<WebArenaEpisode> episodes;
  
  WebArenaResults({
    required this.runId,
    required this.success,
    required this.successRate,
    required this.totalSteps,
    required this.actionCounts,
    required this.episodes,
  });
  
  factory WebArenaResults.fromJson(Map<String, dynamic> json) {
    final List<dynamic> episodesJson = json['episodes'] ?? [];
    
    return WebArenaResults(
      runId: json['run_id'],
      success: json['success'],
      successRate: json['success_rate'].toDouble(),
      totalSteps: json['total_steps'],
      actionCounts: Map<String, int>.from(json['action_counts'] ?? {}),
      episodes: episodesJson.map((e) => WebArenaEpisode.fromJson(e)).toList(),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'run_id': runId,
      'success': success,
      'success_rate': successRate,
      'total_steps': totalSteps,
      'action_counts': actionCounts,
      'episodes': episodes.map((e) => e.toJson()).toList(),
    };
  }
}

/// Model class for WebArena episodes
class WebArenaEpisode {
  final int episodeId;
  final bool success;
  final int steps;
  final Map<String, int> actionCounts;
  final List<WebArenaAction> actions;
  
  WebArenaEpisode({
    required this.episodeId,
    required this.success,
    required this.steps,
    required this.actionCounts,
    required this.actions,
  });
  
  factory WebArenaEpisode.fromJson(Map<String, dynamic> json) {
    final List<dynamic> actionsJson = json['actions'] ?? [];
    
    return WebArenaEpisode(
      episodeId: json['episode_id'],
      success: json['success'],
      steps: json['steps'],
      actionCounts: Map<String, int>.from(json['action_counts'] ?? {}),
      actions: actionsJson.map((a) => WebArenaAction.fromJson(a)).toList(),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'episode_id': episodeId,
      'success': success,
      'steps': steps,
      'action_counts': actionCounts,
      'actions': actions.map((a) => a.toJson()).toList(),
    };
  }
}

/// Model class for WebArena actions
class WebArenaAction {
  final int actionId;
  final String actionType;
  final Map<String, dynamic> actionParams;
  final bool success;
  
  WebArenaAction({
    required this.actionId,
    required this.actionType,
    required this.actionParams,
    required this.success,
  });
  
  factory WebArenaAction.fromJson(Map<String, dynamic> json) {
    return WebArenaAction(
      actionId: json['action_id'],
      actionType: json['action_type'],
      actionParams: Map<String, dynamic>.from(json['action_params'] ?? {}),
      success: json['success'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'action_id': actionId,
      'action_type': actionType,
      'action_params': actionParams,
      'success': success,
    };
  }
}
