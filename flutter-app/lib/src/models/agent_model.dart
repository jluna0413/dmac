/// Agent status enum
enum AgentStatus {
  active,
  inactive,
  training,
  error,
}

/// Agent type enum
enum AgentType {
  developer,
  researcher,
  coordinator,
  analyst,
  creator,
  assistant,
}

/// Agent model
class Agent {
  final String id;
  final String name;
  final String description;
  final AgentType type;
  final AgentStatus status;
  final String? avatarUrl;
  final String modelId;
  final List<String> capabilities;
  final Map<String, dynamic>? metadata;

  Agent({
    required this.id,
    required this.name,
    required this.description,
    required this.type,
    required this.status,
    this.avatarUrl,
    required this.modelId,
    required this.capabilities,
    this.metadata,
  });

  /// Create an agent from JSON
  factory Agent.fromJson(Map<String, dynamic> json) {
    return Agent(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      type: AgentType.values.firstWhere(
        (e) => e.toString() == 'AgentType.${json['type']}',
        orElse: () => AgentType.assistant,
      ),
      status: AgentStatus.values.firstWhere(
        (e) => e.toString() == 'AgentStatus.${json['status']}',
        orElse: () => AgentStatus.inactive,
      ),
      avatarUrl: json['avatar_url'],
      modelId: json['model_id'],
      capabilities: List<String>.from(json['capabilities'] ?? []),
      metadata: json['metadata'],
    );
  }

  /// Convert agent to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'type': type.toString().split('.').last,
      'status': status.toString().split('.').last,
      'avatar_url': avatarUrl,
      'model_id': modelId,
      'capabilities': capabilities,
      'metadata': metadata,
    };
  }

  /// Create a copy of this agent with the given fields replaced
  Agent copyWith({
    String? id,
    String? name,
    String? description,
    AgentType? type,
    AgentStatus? status,
    String? avatarUrl,
    String? modelId,
    List<String>? capabilities,
    Map<String, dynamic>? metadata,
  }) {
    return Agent(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      type: type ?? this.type,
      status: status ?? this.status,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      modelId: modelId ?? this.modelId,
      capabilities: capabilities ?? this.capabilities,
      metadata: metadata ?? this.metadata,
    );
  }
}
