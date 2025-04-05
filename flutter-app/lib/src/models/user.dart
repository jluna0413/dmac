import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

/// User model representing a DMac user
@JsonSerializable()
class User extends Equatable {
  final String id;
  final String name;
  final String email;
  final String? avatarUrl;
  final List<String> roles;
  final DateTime createdAt;
  final DateTime updatedAt;
  
  const User({
    required this.id,
    required this.name,
    required this.email,
    this.avatarUrl,
    required this.roles,
    required this.createdAt,
    required this.updatedAt,
  });
  
  /// Create a User from JSON
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  
  /// Convert User to JSON
  Map<String, dynamic> toJson() => _$UserToJson(this);
  
  /// Check if the user has a specific role
  bool hasRole(String role) => roles.contains(role);
  
  /// Check if the user is an admin
  bool get isAdmin => hasRole('admin');
  
  @override
  List<Object?> get props => [id, name, email, avatarUrl, roles, createdAt, updatedAt];
  
  /// Create a copy of the user with updated fields
  User copyWith({
    String? name,
    String? email,
    String? avatarUrl,
    List<String>? roles,
  }) {
    return User(
      id: id,
      name: name ?? this.name,
      email: email ?? this.email,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      roles: roles ?? this.roles,
      createdAt: createdAt,
      updatedAt: DateTime.now(),
    );
  }
}
