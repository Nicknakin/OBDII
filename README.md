# Branching Convention
## Major Branches

The two major branches are `main` and `testing`

When merging in a branch you will always first pull the latest changes from `testing`, merge `testing` in to your branch, resolve any conflicts, then merge the work in to `testing`.  
The `main` branch will be functional snapshots of the `testing` branch for the purpose of deployments.

## Minor Branches

Branch names have three required components, with one optional component
- Type  
    - feature
    - bugfix
    - style
    - doc
- Initials  
- Description  
- Issue # (Optional)  

The name will match the shape of  
`<Type>/<Initials>/<Description>/<Issue #>`  

Examples  
`feature/nak/center-div`  
`feature/nak/center-div/001` 




# Misc

GROUP Members
1. Chance Huddleston
2. Zain Khan
3. Leonardo Hernandez
4. Zaky Qalawi
5. Nick Kinney


OBD-II Project Sprint 1 Goals
- Gain domain knowledge
- Plan general architecture
- Onboard everyone in to source control system
- Get everyone setup with access to remote server for future testing cloud-based integrations
- Find a good meeting schedule for the group
