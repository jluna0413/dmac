import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:dmac_app/src/services/api_service.dart';
import 'package:dmac_app/src/services/auth_service.dart';
import 'package:dmac_app/src/services/storage_service.dart';
import 'package:dmac_app/src/utils/app_theme.dart';
import 'package:dmac_app/src/screens/splash_screen.dart';

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
  final authService = AuthService(apiService, storageService);

  // Run the app
  runApp(
    MultiProvider(
      providers: [
        Provider<StorageService>.value(value: storageService),
        Provider<ApiService>.value(value: apiService),
        ChangeNotifierProvider<AuthService>.value(value: authService),
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
      home: const SplashScreen(),
    );
  }
}
