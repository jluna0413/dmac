import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/services/mock_auth_service.dart';
import 'package:dmac_app/src/widgets/loading_indicator.dart';
import 'package:dmac_app/src/widgets/material_icon_placeholder.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _errorMessage = null;
    });

    final authService = Provider.of<MockAuthService>(context, listen: false);

    try {
      await authService.login(
        email: _emailController.text.trim(),
        password: _passwordController.text,
      );

      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    }
  }

  Future<void> _loginWithOpenID(String provider) async {
    setState(() {
      _errorMessage = null;
    });

    final authService = Provider.of<MockAuthService>(context, listen: false);

    try {
      await authService.loginWithOpenID(provider: provider);

      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    }
  }

  Future<void> _autoGenerateLogin() async {
    setState(() {
      _errorMessage = null;
    });

    final authService = Provider.of<MockAuthService>(context, listen: false);

    try {
      await authService.autoGenerateLogin();

      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/home');
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<MockAuthService>(context);
    final theme = Theme.of(context);

    return Scaffold(
      body: LoadingContainer(
        isLoading: authService.isLoading,
        loadingMessage: 'Logging in...',
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Logo
                    GradientIconPlaceholder(
                      icon: Icons.psychology,
                      size: 120,
                      gradientColors: [
                        theme.colorScheme.primary,
                        theme.colorScheme.secondary,
                      ],
                      iconColor: Colors.white,
                      label: 'DMac',
                      labelStyle: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    const SizedBox(height: 48),

                    // Title
                    const Text(
                      'Welcome Back',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Sign in to continue',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),

                    // Error message
                    if (_errorMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.error.withAlpha(25),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(color: theme.colorScheme.error),
                          textAlign: TextAlign.center,
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Email field
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        prefixIcon: Icon(Icons.email),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your email';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // Password field
                    TextFormField(
                      controller: _passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        prefixIcon: const Icon(Icons.lock),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword
                                ? Icons.visibility
                                : Icons.visibility_off,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscurePassword = !_obscurePassword;
                            });
                          },
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 8),

                    // Forgot password
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () {
                          // Navigate to forgot password screen
                        },
                        child: const Text('Forgot Password?'),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Login button
                    ElevatedButton(
                      onPressed: _login,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: const Text(
                        'Sign In',
                        style: TextStyle(fontSize: 16),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Divider
                    Row(
                      children: [
                        const Expanded(child: Divider()),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Text(
                            'OR',
                            style: theme.textTheme.bodyMedium,
                          ),
                        ),
                        const Expanded(child: Divider()),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // OpenID login buttons
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildOpenIDButton(
                          icon: Icons.g_mobiledata,
                          label: 'Google',
                          color: Colors.red,
                          onPressed: () => _loginWithOpenID('google'),
                        ),
                        _buildOpenIDButton(
                          icon: Icons.apple,
                          label: 'Apple',
                          color: Colors.black,
                          onPressed: () => _loginWithOpenID('apple'),
                        ),
                        _buildOpenIDButton(
                          icon: Icons.code,
                          label: 'GitHub',
                          color: Colors.purple,
                          onPressed: () => _loginWithOpenID('github'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Auto-generate login button
                    OutlinedButton.icon(
                      onPressed: _autoGenerateLogin,
                      icon: const Icon(Icons.auto_awesome),
                      label: const Text('Auto-Generate Login (For Testing)'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Test account info
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Test Accounts',
                              style: theme.textTheme.titleMedium,
                            ),
                            const SizedBox(height: 8),
                            _buildTestAccountInfo(
                              email: 'admin@dmac.ai',
                              password: 'any password works',
                              role: 'Admin',
                            ),
                            const Divider(),
                            _buildTestAccountInfo(
                              email: 'user@dmac.ai',
                              password: 'any password works',
                              role: 'User',
                            ),
                            const Divider(),
                            _buildTestAccountInfo(
                              email: 'dev@dmac.ai',
                              password: 'any password works',
                              role: 'Developer',
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Register link
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text("Don't have an account?"),
                        TextButton(
                          onPressed: () {
                            // Navigate to register screen
                          },
                          child: const Text('Sign Up'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildOpenIDButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onPressed,
  }) {
    return Column(
      children: [
        IconButton(
          onPressed: onPressed,
          icon: Icon(icon, color: color),
          iconSize: 32,
        ),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }

  Widget _buildTestAccountInfo({
    required String email,
    required String password,
    required String role,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('$role Account:',
            style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Row(
          children: [
            const Text('Email: ',
                style: TextStyle(fontWeight: FontWeight.bold)),
            Text(email),
            IconButton(
              icon: const Icon(Icons.copy, size: 16),
              onPressed: () {
                _emailController.text = email;
                _passwordController.text = 'password';
              },
              tooltip: 'Use this account',
            ),
          ],
        ),
        Row(
          children: [
            const Text('Password: ',
                style: TextStyle(fontWeight: FontWeight.bold)),
            Text(password),
          ],
        ),
      ],
    );
  }
}
