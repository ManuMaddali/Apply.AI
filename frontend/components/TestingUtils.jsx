import React, { useState, useCallback } from 'react';
import { testResumes } from '../data/testResumes';
import { testScenarios } from '../data/testJobUrls';

export default function TestingUtils({ onRunBatchTest, onRunPerformanceTest }) {
  const [batchTestConfig, setBatchTestConfig] = useState({
    scenarios: [],
    includeMetrics: true,
    saveResults: true,
    parallelRuns: 1
  });
  const [performanceConfig, setPerformanceConfig] = useState({
    scenario: '',
    iterations: 3,
    measureLatency: true,
    measureMemory: true
  });
  const [testResults, setTestResults] = useState([]);
  const [isRunning, setIsRunning] = useState(false);

  // Batch testing functionality
  const handleBatchTest = useCallback(async () => {
    if (batchTestConfig.scenarios.length === 0) {
      alert('Please select at least one scenario for batch testing');
      return;
    }

    setIsRunning(true);
    const results = [];

    try {
      for (const scenarioId of batchTestConfig.scenarios) {
        const scenario = testScenarios.find(s => s.id === scenarioId);
        if (!scenario) continue;

        console.log(`Running batch test for scenario: ${scenario.name}`);
        
        // Here you would call your actual testing function
        const startTime = performance.now();
        
        // Simulate API call (replace with actual onRunBatchTest call)
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const endTime = performance.now();
        const duration = endTime - startTime;

        results.push({
          scenarioId,
          scenarioName: scenario.name,
          duration,
          success: true,
          timestamp: new Date().toISOString()
        });
      }

      setTestResults(results);
      console.log('Batch test completed:', results);
    } catch (error) {
      console.error('Batch test failed:', error);
    } finally {
      setIsRunning(false);
    }
  }, [batchTestConfig]);

  // Performance testing functionality
  const handlePerformanceTest = useCallback(async () => {
    if (!performanceConfig.scenario) {
      alert('Please select a scenario for performance testing');
      return;
    }

    setIsRunning(true);
    const results = [];

    try {
      for (let i = 0; i < performanceConfig.iterations; i++) {
        console.log(`Performance test iteration ${i + 1}/${performanceConfig.iterations}`);
        
        const startTime = performance.now();
        const startMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
        
        // Simulate API call (replace with actual onRunPerformanceTest call)
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const endTime = performance.now();
        const endMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
        
        results.push({
          iteration: i + 1,
          latency: endTime - startTime,
          memoryDelta: endMemory - startMemory,
          timestamp: new Date().toISOString()
        });
      }

      // Calculate averages
      const avgLatency = results.reduce((sum, r) => sum + r.latency, 0) / results.length;
      const avgMemory = results.reduce((sum, r) => sum + r.memoryDelta, 0) / results.length;

      setTestResults([{
        type: 'performance',
        scenario: performanceConfig.scenario,
        iterations: performanceConfig.iterations,
        avgLatency: avgLatency.toFixed(2),
        avgMemory: avgMemory.toFixed(2),
        results
      }]);

      console.log('Performance test completed:', { avgLatency, avgMemory });
    } catch (error) {
      console.error('Performance test failed:', error);
    } finally {
      setIsRunning(false);
    }
  }, [performanceConfig]);

  return (
    <div className="bg-white/80 backdrop-blur-light rounded-xl p-6 border border-gray-200">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Advanced Testing Utilities</h2>
      
      <div className="space-y-6">
        {/* Batch Testing */}
        <div>
          <h3 className="text-md font-medium text-gray-700 mb-3">Batch Testing</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Select Scenarios
              </label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                {testScenarios.map(scenario => (
                  <label key={scenario.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={batchTestConfig.scenarios.includes(scenario.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setBatchTestConfig(prev => ({
                            ...prev,
                            scenarios: [...prev.scenarios, scenario.id]
                          }));
                        } else {
                          setBatchTestConfig(prev => ({
                            ...prev,
                            scenarios: prev.scenarios.filter(id => id !== scenario.id)
                          }));
                        }
                      }}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-xs text-gray-600">{scenario.name}</span>
                  </label>
                ))}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={batchTestConfig.includeMetrics}
                  onChange={(e) => setBatchTestConfig(prev => ({
                    ...prev,
                    includeMetrics: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-600">Include Metrics</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={batchTestConfig.saveResults}
                  onChange={(e) => setBatchTestConfig(prev => ({
                    ...prev,
                    saveResults: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-600">Save Results</span>
              </label>
            </div>

            <button
              onClick={handleBatchTest}
              disabled={isRunning || batchTestConfig.scenarios.length === 0}
              className="w-full bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white py-2 px-4 rounded-lg transition-colors text-sm"
            >
              {isRunning ? 'Running Batch Test...' : `Run Batch Test (${batchTestConfig.scenarios.length} scenarios)`}
            </button>
          </div>
        </div>

        {/* Performance Testing */}
        <div>
          <h3 className="text-md font-medium text-gray-700 mb-3">Performance Testing</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Test Scenario
              </label>
              <select
                value={performanceConfig.scenario}
                onChange={(e) => setPerformanceConfig(prev => ({
                  ...prev,
                  scenario: e.target.value
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              >
                <option value="">Select scenario for performance testing...</option>
                {testScenarios.map(scenario => (
                  <option key={scenario.id} value={scenario.id}>
                    {scenario.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Iterations: {performanceConfig.iterations}
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={performanceConfig.iterations}
                onChange={(e) => setPerformanceConfig(prev => ({
                  ...prev,
                  iterations: parseInt(e.target.value)
                }))}
                className="w-full"
              />
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={performanceConfig.measureLatency}
                  onChange={(e) => setPerformanceConfig(prev => ({
                    ...prev,
                    measureLatency: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-600">Measure Latency</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={performanceConfig.measureMemory}
                  onChange={(e) => setPerformanceConfig(prev => ({
                    ...prev,
                    measureMemory: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-600">Measure Memory</span>
              </label>
            </div>

            <button
              onClick={handlePerformanceTest}
              disabled={isRunning || !performanceConfig.scenario}
              className="w-full bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white py-2 px-4 rounded-lg transition-colors text-sm"
            >
              {isRunning ? 'Running Performance Test...' : 'Run Performance Test'}
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <h3 className="text-md font-medium text-gray-700 mb-3">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setBatchTestConfig(prev => ({
                ...prev,
                scenarios: testScenarios.slice(0, 3).map(s => s.id)
              }))}
              className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 py-2 px-3 rounded-lg transition-colors"
            >
              Select Top 3
            </button>
            <button
              onClick={() => setBatchTestConfig(prev => ({
                ...prev,
                scenarios: testScenarios.map(s => s.id)
              }))}
              className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 py-2 px-3 rounded-lg transition-colors"
            >
              Select All
            </button>
            <button
              onClick={() => setPerformanceConfig(prev => ({
                ...prev,
                scenario: 'entry_level_swe_big_tech'
              }))}
              className="text-xs bg-orange-100 hover:bg-orange-200 text-orange-700 py-2 px-3 rounded-lg transition-colors"
            >
              Quick Perf Test
            </button>
            <button
              onClick={() => {
                setBatchTestConfig({
                  scenarios: [],
                  includeMetrics: true,
                  saveResults: true,
                  parallelRuns: 1
                });
                setPerformanceConfig({
                  scenario: '',
                  iterations: 3,
                  measureLatency: true,
                  measureMemory: true
                });
                setTestResults([]);
              }}
              className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-3 rounded-lg transition-colors"
            >
              Reset All
            </button>
          </div>
        </div>

        {/* Test Results */}
        {testResults.length > 0 && (
          <div>
            <h3 className="text-md font-medium text-gray-700 mb-3">Test Results</h3>
            <div className="max-h-40 overflow-y-auto space-y-2">
              {testResults.map((result, index) => (
                <div key={index} className="bg-gray-50 p-3 rounded-lg">
                  {result.type === 'performance' ? (
                    <div>
                      <p className="text-sm font-medium text-gray-700">
                        Performance Test: {result.scenario}
                      </p>
                      <p className="text-xs text-gray-600">
                        Avg Latency: {result.avgLatency}ms | Avg Memory: {result.avgMemory}B
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm font-medium text-gray-700">
                        {result.scenarioName}
                      </p>
                      <p className="text-xs text-gray-600">
                        Duration: {result.duration.toFixed(2)}ms | 
                        Status: {result.success ? '✅ Success' : '❌ Failed'}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            <button
              onClick={() => {
                const dataStr = JSON.stringify(testResults, null, 2);
                const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                const exportFileDefaultName = `test-results-${new Date().toISOString().split('T')[0]}.json`;
                const linkElement = document.createElement('a');
                linkElement.setAttribute('href', dataUri);
                linkElement.setAttribute('download', exportFileDefaultName);
                linkElement.click();
              }}
              className="mt-3 w-full bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors text-sm"
            >
              Export Results
            </button>
          </div>
        )}
      </div>
    </div>
  );
} 