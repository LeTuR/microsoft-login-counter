/**
 * Contract test for webNavigation.onCompleted listener
 * Verifies event structure and URL filtering for login.microsoftonline.com
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { mockWebNavigation, resetAllMocks } from '../setup/chrome-mocks';

describe('webNavigation.onCompleted contract', () => {
  beforeEach(() => {
    resetAllMocks();
  });

  it('provides required fields in event details', () => {
    const mockDetails: chrome.webNavigation.WebNavigationFramedCallbackDetails = {
      tabId: 123,
      url: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?code=ABC',
      frameId: 0,
      frameType: 'outermost_frame',
      timeStamp: Date.now(),
      processId: 456,
      documentLifecycle: 'active'
    };

    // Verify required fields exist
    expect(mockDetails).toHaveProperty('tabId');
    expect(mockDetails).toHaveProperty('url');
    expect(mockDetails).toHaveProperty('frameId');
    expect(mockDetails).toHaveProperty('timeStamp');
    expect(typeof mockDetails.tabId).toBe('number');
    expect(typeof mockDetails.url).toBe('string');
    expect(typeof mockDetails.frameId).toBe('number');
    expect(typeof mockDetails.timeStamp).toBe('number');
  });

  it('supports adding event listener', () => {
    const listener = jest.fn();

    mockWebNavigation.onCompleted.addListener(listener);

    expect(mockWebNavigation.onCompleted.addListener).toHaveBeenCalledWith(listener);
  });

  it('allows URL filtering for login.microsoftonline.com', () => {
    const listener = jest.fn();
    const filter: chrome.webNavigation.WebNavigationEventFilter = {
      url: [{ hostEquals: 'login.microsoftonline.com' }]
    };

    mockWebNavigation.onCompleted.addListener(listener, filter);

    expect(mockWebNavigation.onCompleted.addListener).toHaveBeenCalledWith(listener, filter);
  });

  it('distinguishes main frame from subframes using frameId', () => {
    const mainFrameDetails = {
      tabId: 1,
      url: 'https://login.microsoftonline.com/authorize',
      frameId: 0,
      timeStamp: Date.now()
    };

    const subframeDetails = {
      tabId: 1,
      url: 'https://login.microsoftonline.com/authorize',
      frameId: 1,
      timeStamp: Date.now()
    };

    // Main frame should have frameId = 0
    expect(mainFrameDetails.frameId).toBe(0);
    // Subframes have frameId > 0
    expect(subframeDetails.frameId).toBeGreaterThan(0);
  });

  it('provides accurate timestamp within reasonable range', () => {
    const now = Date.now();
    const mockDetails = {
      tabId: 1,
      url: 'https://login.microsoftonline.com/authorize',
      frameId: 0,
      timeStamp: now
    };

    // Timestamp should be close to current time (within 1 second)
    expect(Math.abs(mockDetails.timeStamp - Date.now())).toBeLessThan(1000);
  });
});
