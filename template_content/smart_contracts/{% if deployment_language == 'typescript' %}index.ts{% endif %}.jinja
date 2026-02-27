import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath, pathToFileURL } from 'url'
import { consoleLogger } from '@algorandfoundation/algokit-utils/types/logging'
import { Config } from '@algorandfoundation/algokit-utils'
// import { registerDebugEventHandlers } from '@algorandfoundation/algokit-utils-debug' // Uncomment to enable persisting artifacts required by AlgoKit AVM Debugger

// Uncomment the debug and traceAll options to enable auto generation of AVM Debugger compliant sourceMap and simulation trace file.
// Learn more about using AlgoKit AVM Debugger to debug your TEAL source codes and inspect various kinds of Algorand transactions in atomic groups -> https://github.com/algorandfoundation/algokit-avm-vscode-Debugger

Config.configure({
  logger: consoleLogger,
  //  debug: true,
  //  traceAll: true,
})
// registerDebugEventHandlers() // Uncomment to enable persisting artifacts required by AlgoKit AVM Debugger

// base directory
const baseDir = path.dirname(fileURLToPath(import.meta.url))

// function to validate and dynamically import a module
async function importDeployerIfExists(dir: string) {
  const tsPath = path.resolve(dir, 'deploy-config.ts')
  const jsPath = path.resolve(dir, 'deploy-config.js')
  const deployerPath = fs.existsSync(tsPath) ? tsPath : fs.existsSync(jsPath) ? jsPath : undefined

  if (deployerPath) {
    const deployer = await import(pathToFileURL(deployerPath).href)
    return { ...deployer, name: path.basename(dir) }
  }
  return null
}

// get a list of all deployers from the subdirectories
async function getDeployers() {
  const directories = fs
    .readdirSync(baseDir, { withFileTypes: true })
    .filter((dirent) => dirent.isDirectory())
    .map((dirent) => path.resolve(baseDir, dirent.name))

  const deployers = await Promise.all(directories.map(importDeployerIfExists))
  return deployers.filter((deployer) => deployer !== null) // Filter out null values
}

// execute all the deployers
(async () => {
  const contractName = process.argv.length > 2 ? process.argv[2] : undefined
  const contractDeployers = await getDeployers()
  
  const filteredDeployers = contractName
    ? contractDeployers.filter(deployer => deployer.name === contractName)
    : contractDeployers

  if (contractName && filteredDeployers.length === 0) {
    console.warn(`No deployer found for contract name: ${contractName}`)
    return
  }

  for (const deployer of filteredDeployers) {
    try {
      await deployer.deploy()
    } catch (e) {
      console.error(`Error deploying ${deployer.name}:`, e)
    }
  }
})()
