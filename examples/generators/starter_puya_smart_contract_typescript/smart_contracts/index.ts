import * as fs from 'fs'
import * as path from 'path'
import { consoleLogger } from '@algorandfoundation/algokit-utils/types/logging'
import * as algokit from '@algorandfoundation/algokit-utils'

// Uncomment the debug and traceAll options to enable auto generation of AVM Debugger compliant sourceMap and simulation trace file.
// Learn more about using AlgoKit AVM Debugger to debug your TEAL source codes and inspect various kinds of Algorand transactions in atomic groups -> https://github.com/algorandfoundation/algokit-avm-vscode-Debugger

algokit.Config.configure({
  logger: consoleLogger,
  //  debug: true,
  //  traceAll: true,
})

// base directory
const baseDir = path.resolve(__dirname)

// function to validate and dynamically import a module
async function importDeployerIfExists(dir: string) {
  const deployerPath = path.resolve(dir, 'deploy-config')
  if (fs.existsSync(deployerPath + '.ts') || fs.existsSync(deployerPath + '.js')) {
    const deployer = await import(deployerPath)
    return deployer.deploy
  }
}

// get a list of all deployers from the subdirectories
async function getDeployers() {
  const directories = fs.readdirSync(baseDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => path.resolve(baseDir, dirent.name))

  return Promise.all(directories.map(importDeployerIfExists))
}

// execute all the deployers
(async () => {
  const contractDeployers = (await getDeployers()).filter(Boolean)

  for (const deployer of contractDeployers) {
    try {
      await deployer()
    } catch (e) {
      console.error(e)
    }
  }
})()
