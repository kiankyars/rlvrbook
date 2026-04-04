# Practical Verifier Design Checklist

## Purpose

This appendix should read like a field manual that can be pasted into internal docs or shared directly in lab discussions.

## Checklist

1. What exact object is being verified?
2. What evidence does the verifier actually consume?
3. Which important properties remain off-screen?
4. Where are the obvious attack surfaces?
5. Which failures are silent rather than visible?
6. How will robustness be audited before large-scale optimization?
7. What deployment constraints shape the acceptable verifier stack?
