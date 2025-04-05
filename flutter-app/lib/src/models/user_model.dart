/// User role enum
enum UserRole {
  user,
  admin,
  developer,
}

/// User model
class User {
  final String id;
  final String email;
  final String name;
  final UserRole role;
  final String? avatarUrl;
  final Map<String, dynamic>? metadata;

  User({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
    this.avatarUrl,
    this.metadata,
  });

  /// Create a user from JSON
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      name: json['name'],
      role: UserRole.values.firstWhere(
        (e) => e.toString() == 'UserRole.${json['role']}',
        orElse: () => UserRole.user,
      ),
      avatarUrl: json['avatar_url'],
      metadata: json['metadata'],
    );
  }

  /// Convert user to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'role': role.toString().split('.').last,
      'avatar_url': avatarUrl,
      'metadata': metadata,
    };
  }

  /// Create a copy of this user with the given fields replaced
  User copyWith({
    String? id,
    String? email,
    String? name,
    UserRole? role,
    String? avatarUrl,
    Map<String, dynamic>? metadata,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      name: name ?? this.name,
      role: role ?? this.role,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      metadata: metadata ?? this.metadata,
    );
  }
}
