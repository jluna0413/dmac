/// Model provider enum
enum ModelProvider {
  ollama,
  openAI,
  anthropic,
  google,
  local,
  custom,
}

/// Model type enum
enum ModelType {
  text,
  image,
  audio,
  multimodal,
}

/// Model status enum
enum ModelStatus {
  available,
  downloading,
  training,
  error,
}

/// Model model
class AIModel {
  final String id;
  final String name;
  final String description;
  final ModelProvider provider;
  final ModelType type;
  final ModelStatus status;
  final int? parameterCount; // in billions
  final String? version;
  final Map<String, dynamic>? benchmarks;
  final Map<String, dynamic>? metadata;

  AIModel({
    required this.id,
    required this.name,
    required this.description,
    required this.provider,
    required this.type,
    required this.status,
    this.parameterCount,
    this.version,
    this.benchmarks,
    this.metadata,
  });

  /// Create a model from JSON
  factory AIModel.fromJson(Map<String, dynamic> json) {
    return AIModel(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      provider: ModelProvider.values.firstWhere(
        (e) => e.toString() == 'ModelProvider.${json['provider']}',
        orElse: () => ModelProvider.custom,
      ),
      type: ModelType.values.firstWhere(
        (e) => e.toString() == 'ModelType.${json['type']}',
        orElse: () => ModelType.text,
      ),
      status: ModelStatus.values.firstWhere(
        (e) => e.toString() == 'ModelStatus.${json['status']}',
        orElse: () => ModelStatus.available,
      ),
      parameterCount: json['parameter_count'],
      version: json['version'],
      benchmarks: json['benchmarks'],
      metadata: json['metadata'],
    );
  }

  /// Convert model to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'provider': provider.toString().split('.').last,
      'type': type.toString().split('.').last,
      'status': status.toString().split('.').last,
      'parameter_count': parameterCount,
      'version': version,
      'benchmarks': benchmarks,
      'metadata': metadata,
    };
  }

  /// Create a copy of this model with the given fields replaced
  AIModel copyWith({
    String? id,
    String? name,
    String? description,
    ModelProvider? provider,
    ModelType? type,
    ModelStatus? status,
    int? parameterCount,
    String? version,
    Map<String, dynamic>? benchmarks,
    Map<String, dynamic>? metadata,
  }) {
    return AIModel(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      provider: provider ?? this.provider,
      type: type ?? this.type,
      status: status ?? this.status,
      parameterCount: parameterCount ?? this.parameterCount,
      version: version ?? this.version,
      benchmarks: benchmarks ?? this.benchmarks,
      metadata: metadata ?? this.metadata,
    );
  }
}
