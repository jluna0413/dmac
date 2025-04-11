/**
 * Laminar Service for MaCoder
 * 
 * This service provides integration with Laminar for tracing and evaluation.
 */

import * as vscode from 'vscode';
import { Laminar, observe } from '@lmnr-ai/lmnr';

export class LaminarService {
    private static instance: LaminarService;
    private initialized: boolean = false;
    private enabled: boolean = false;

    private constructor() {
        // Private constructor for singleton pattern
    }

    /**
     * Get the singleton instance of the LaminarService
     */
    public static getInstance(): LaminarService {
        if (!LaminarService.instance) {
            LaminarService.instance = new LaminarService();
        }
        return LaminarService.instance;
    }

    /**
     * Initialize the Laminar service
     */
    public async initialize(): Promise<void> {
        if (this.initialized) {
            return;
        }

        const config = vscode.workspace.getConfiguration('macoder.laminar');
        this.enabled = config.get<boolean>('enabled', true);

        if (!this.enabled) {
            console.log('Laminar integration is disabled');
            return;
        }

        try {
            const projectApiKey = config.get<string>('projectApiKey', '');
            const baseUrl = config.get<string>('baseUrl', 'https://api.lmnr.ai');
            const selfHosted = config.get<boolean>('selfHosted', false);

            if (!projectApiKey) {
                console.warn('Laminar project API key not provided. Laminar integration will be disabled.');
                this.enabled = false;
                return;
            }

            if (selfHosted) {
                Laminar.initialize({
                    projectApiKey,
                    baseUrl,
                    httpPort: 8000,
                    grpcPort: 8001
                });
            } else {
                Laminar.initialize({ projectApiKey });
            }

            console.log('Laminar initialized successfully');
            this.initialized = true;
        } catch (error) {
            console.error('Failed to initialize Laminar:', error);
            this.enabled = false;
        }
    }

    /**
     * Check if Laminar is enabled
     */
    public isEnabled(): boolean {
        return this.enabled && this.initialized;
    }

    /**
     * Trace a function using Laminar
     * @param name The name of the trace
     * @param func The function to trace
     * @param args The arguments to pass to the function
     * @returns The result of the function
     */
    public async trace<T>(name: string, func: (...args: any[]) => Promise<T>, ...args: any[]): Promise<T> {
        if (!this.isEnabled()) {
            return await func(...args);
        }

        return await observe(
            { name },
            async () => {
                return await func(...args);
            }
        );
    }

    /**
     * Create a span for manual tracing
     * @param name The name of the span
     * @param attributes Optional attributes for the span
     */
    public createSpan(name: string, attributes: Record<string, any> = {}): any {
        if (!this.isEnabled()) {
            // Return a dummy context manager
            return {
                setAttributes: (attrs: Record<string, any>) => {},
                addEvent: (name: string, attrs?: Record<string, any>) => {},
                end: () => {}
            };
        }

        // Import OpenTelemetry API
        const { trace } = require('@opentelemetry/api');
        const tracer = trace.getTracer('macoder');
        return tracer.startSpan(name, { attributes });
    }

    /**
     * Add data to a Laminar dataset
     * @param datasetName The name of the dataset
     * @param dataPoint The data point to add
     * @param target Optional target for the data point
     */
    public async addToDataset(
        datasetName: string, 
        dataPoint: Record<string, any>, 
        target?: Record<string, any>
    ): Promise<boolean> {
        if (!this.isEnabled()) {
            return false;
        }

        try {
            const { LaminarDataset } = require('@lmnr-ai/lmnr');
            const dataset = new LaminarDataset(datasetName);
            
            await dataset.addDatapoint({
                data: dataPoint,
                target: target || {}
            });
            
            return true;
        } catch (error) {
            console.error('Failed to add to dataset:', error);
            return false;
        }
    }

    /**
     * Evaluate a function using Laminar
     * @param data The data to evaluate
     * @param executor The function to execute
     * @param evaluators The evaluators to use
     * @param groupId Optional group ID for the evaluation
     */
    public async evaluate(
        data: any, 
        executor: (data: any) => any, 
        evaluators: Record<string, (output: any, target: any) => number>,
        groupId?: string
    ): Promise<Record<string, any>> {
        if (!this.isEnabled()) {
            return { error: 'Laminar not enabled' };
        }

        try {
            const { evaluate } = require('@lmnr-ai/lmnr');
            
            const result = await evaluate({
                data,
                executor,
                evaluators,
                groupId
            });
            
            return result;
        } catch (error) {
            console.error('Failed to evaluate with Laminar:', error);
            return { error: String(error) };
        }
    }
}
