/// Task status enum
enum TaskStatus {
  todo,
  inProgress,
  completed,
  blocked,
}

/// Task priority enum
enum TaskPriority {
  low,
  medium,
  high,
}

/// Task filter enum
enum TaskFilter {
  all,
  todo,
  inProgress,
  completed,
  blocked,
}

/// Task model
class Task {
  final String id;
  final String title;
  final String description;
  final TaskStatus status;
  final TaskPriority priority;
  final String assignedAgentId;
  final DateTime createdAt;
  final DateTime dueDate;
  final DateTime? completedAt;
  final List<String> tags;
  final Map<String, dynamic>? metadata;

  Task({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.priority,
    required this.assignedAgentId,
    required this.createdAt,
    required this.dueDate,
    this.completedAt,
    required this.tags,
    this.metadata,
  });

  /// Create a task from JSON
  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      status: TaskStatus.values.firstWhere(
        (e) => e.toString() == 'TaskStatus.${json['status']}',
        orElse: () => TaskStatus.todo,
      ),
      priority: TaskPriority.values.firstWhere(
        (e) => e.toString() == 'TaskPriority.${json['priority']}',
        orElse: () => TaskPriority.medium,
      ),
      assignedAgentId: json['assigned_agent_id'],
      createdAt: DateTime.parse(json['created_at']),
      dueDate: DateTime.parse(json['due_date']),
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : null,
      tags: List<String>.from(json['tags'] ?? []),
      metadata: json['metadata'],
    );
  }

  /// Convert task to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'status': status.toString().split('.').last,
      'priority': priority.toString().split('.').last,
      'assigned_agent_id': assignedAgentId,
      'created_at': createdAt.toIso8601String(),
      'due_date': dueDate.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'tags': tags,
      'metadata': metadata,
    };
  }

  /// Create a copy of this task with the given fields replaced
  Task copyWith({
    String? id,
    String? title,
    String? description,
    TaskStatus? status,
    TaskPriority? priority,
    String? assignedAgentId,
    DateTime? createdAt,
    DateTime? dueDate,
    DateTime? completedAt,
    List<String>? tags,
    Map<String, dynamic>? metadata,
  }) {
    return Task(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      status: status ?? this.status,
      priority: priority ?? this.priority,
      assignedAgentId: assignedAgentId ?? this.assignedAgentId,
      createdAt: createdAt ?? this.createdAt,
      dueDate: dueDate ?? this.dueDate,
      completedAt: completedAt ?? this.completedAt,
      tags: tags ?? this.tags,
      metadata: metadata ?? this.metadata,
    );
  }
}
