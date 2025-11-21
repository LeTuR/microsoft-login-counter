/**
 * Chrome API mocks for Jest testing
 * Mocks chrome.storage.local and chrome.webNavigation APIs
 */

interface StorageData {
  [key: string]: any;
}

const storageData: StorageData = {};

// Mock chrome.storage.local
const mockStorageLocal = {
  get: jest.fn((keys?: string | string[] | null) => {
    if (!keys) {
      return Promise.resolve({ ...storageData });
    }
    if (typeof keys === 'string') {
      return Promise.resolve({ [keys]: storageData[keys] });
    }
    if (Array.isArray(keys)) {
      const result: StorageData = {};
      keys.forEach(key => {
        if (key in storageData) {
          result[key] = storageData[key];
        }
      });
      return Promise.resolve(result);
    }
    return Promise.resolve({});
  }),

  set: jest.fn((items: StorageData) => {
    Object.assign(storageData, items);
    return Promise.resolve();
  }),

  clear: jest.fn(() => {
    Object.keys(storageData).forEach(key => delete storageData[key]);
    return Promise.resolve();
  }),

  getBytesInUse: jest.fn((keys?: string | string[] | null) => {
    let data = storageData;
    if (keys) {
      const keysArray = Array.isArray(keys) ? keys : [keys];
      data = {};
      keysArray.forEach(key => {
        if (key in storageData) {
          data[key] = storageData[key];
        }
      });
    }
    const size = JSON.stringify(data).length;
    return Promise.resolve(size);
  })
};

// Mock chrome.webNavigation
const mockWebNavigation = {
  onCompleted: {
    addListener: jest.fn(),
    removeListener: jest.fn(),
    hasListener: jest.fn()
  }
};

// Mock chrome.runtime
const mockRuntime = {
  onInstalled: {
    addListener: jest.fn(),
    removeListener: jest.fn(),
    hasListener: jest.fn()
  },
  lastError: undefined as chrome.runtime.LastError | undefined
};

// Attach mocks to global chrome object
(global as any).chrome = {
  storage: {
    local: mockStorageLocal
  },
  webNavigation: mockWebNavigation,
  runtime: mockRuntime
};

// Export for direct access in tests
export { mockStorageLocal, mockWebNavigation, mockRuntime };

// Helper to clear storage between tests
export function clearMockStorage(): void {
  Object.keys(storageData).forEach(key => delete storageData[key]);
}

// Helper to reset all mocks
export function resetAllMocks(): void {
  clearMockStorage();
  jest.clearAllMocks();
}
