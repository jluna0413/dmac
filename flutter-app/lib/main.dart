import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/services/api_service.dart';
import 'package:dmac_app/src/services/mock_auth_service.dart';
import 'package:dmac_app/src/services/storage_service.dart';
import 'package:dmac_app/src/services/reinforcement_learning_service.dart';
import 'package:dmac_app/src/services/deep_research_service.dart';
import 'package:dmac_app/src/utils/app_theme.dart';
import 'package:dmac_app/src/screens/splash_screen.dart';
import 'package:dmac_app/src/screens/home_screen.dart';
import 'package:dmac_app/src/screens/admin/admin_dashboard.dart';
import 'package:dmac_app/src/screens/auth/login_screen_new.dart';
import 'package:dmac_app/src/screens/onboarding_screen.dart';
import 'package:dmac_app/src/screens/dashboard/dashboard_screen.dart';
import 'package:dmac_app/src/screens/chat/chat_screen.dart';
import 'package:dmac_app/src/screens/webarena_screen.dart';

void main() async {
  // Ensure Flutter is initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);

  // Initialize services
  final storageService = await StorageService.init();
  final apiService = ApiService();
  final authService = MockAuthService();
  final rlService = ReinforcementLearningService();
  final deepResearchService = DeepResearchService();

  // Run the app
  runApp(
    MultiProvider(
      providers: [
        Provider<StorageService>.value(value: storageService),
        Provider<ApiService>.value(value: apiService),
        Provider<ReinforcementLearningService>.value(value: rlService),
        Provider<DeepResearchService>.value(value: deepResearchService),
        ChangeNotifierProvider<MockAuthService>.value(value: authService),
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
      ],
      child: const DMacApp(),
    ),
  );
}

class DMacApp extends StatelessWidget {
  const DMacApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);

    return MaterialApp(
      title: 'DMac AI Agent Swarm',
      theme: themeProvider.lightTheme,
      darkTheme: themeProvider.darkTheme,
      themeMode: themeProvider.themeMode,
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/home': (context) => const HomeScreen(),
        '/dashboard': (context) => const DashboardScreen(),
        '/admin': (context) => const AdminDashboard(),
        '/login': (context) => const LoginScreen(),
        '/onboarding': (context) => const OnboardingScreen(),
        '/chat': (context) => const ChatScreen(),
        '/webarena': (context) => const WebArenaScreen(),
      },
    );
  }
}
