#ifndef GLUON_SETTINGS_JAVASCRIPT_H
#define GLUON_SETTINGS_JAVASCRIPT_H
// Keep UI availability aligned with native explicit choices. AppDetails may
// report an empty resolved name for an unavailable chosen tool, so app-priority
// entries take precedence even when their name is empty. Windows-only defaults
// must remain usable without relying on an explicit Gluon mapping being present.
#define GLUON_INVALID_OS_GETTER \
    "get is_invalid_os_type(){const bad=this.most_available_per_client_data?.is_invalid_os_type;if(!bad)return false;" \
    "const p=globalThis.__NOTPROTON_NATIVE_PLATFORM__,d=globalThis.appDetailsStore?.GetAppDetails(this.appid)," \
    "n=d?.strCompatToolName||\"\",gluon=/^(gluon|gluon-proton)$/.test(n),explicit=d?.nCompatToolPriority>=250;" \
    "if(n===\"gluon.none\"||explicit&&!gluon)return true;if(gluon)return false;if(n)return true;" \
    "if(p?.windowsLaunchOnly?.has(this.appid)||p?.windows?.has(this.appid)&&!p.mac?.has(this.appid))return false;" \
    "return !(globalThis.__GLUON_SETTINGS__?.effectiveMac32&&p?.mac32?.has(this.appid))}"

// An actual Settings section, using the page's JSX runtime and an accessible
// switch. The native command never writes a Steam compatibility mapping.
#define GLUON_SETTINGS_SCRIPT \
    "globalThis.__GLUON_SETTINGS__.status=()=>globalThis.__GLUON_SETTINGS__.effectiveMac32?\"Automatic 32-bit Mac support is active.\":\"Automatic 32-bit Mac support is off.\";" \
    "if(typeof globalThis.addEventListener===\"function\"&&!globalThis.__GLUON_SETTINGS__.listening){globalThis.__GLUON_SETTINGS__.listening=true;" \
    "globalThis.addEventListener(\"storage\",e=>{if(e.key!==\"gluon.mac32.changed\"||!e.newValue)return;const s=globalThis.__GLUON_SETTINGS__;" \
    "s.autoMac32=s.effectiveMac32=e.newValue.startsWith(\"1:\");const t=globalThis.document?.querySelector('input[name=gluon_auto_mac32]');" \
    "if(t){t.checked=s.effectiveMac32;t.closest(\"div\")?.querySelector(\"[role=status]\")?.replaceChildren(s.status())}})};" \
    "globalThis.__GLUON_SETTINGS__.render=J=>J(\"div\",{style:{padding:\"12px 0\"},children:[" \
    "J(\"label\",{style:{display:\"flex\",alignItems:\"center\",gap:12,cursor:\"pointer\"},children:[" \
    "J(\"input\",{type:\"checkbox\",role:\"switch\",name:\"gluon_auto_mac32\",defaultChecked:globalThis.__GLUON_SETTINGS__.autoMac32," \
    "onChange:async e=>{const t=e.currentTarget,v=t.checked,s=t.closest(\"div\").querySelector(\"[role=status]\");" \
    "t.disabled=true;try{const f=globalThis.__GLUON_SETTINGS__.specifyVerified||globalThis.__GLUON_SETTINGS__.specify||(typeof globalThis.SteamClient?.Apps?.SpecifyCompatTool===\"function\"?n=>SteamClient.Apps.SpecifyCompatTool(0,n):null);if(!f)throw Error();" \
    "const r=await f(v?\"__gluon_settings_mac32_on_v1\":\"__gluon_settings_mac32_off_v1\");" \
    "if(r===false||r?.success===false)throw Error();const g=globalThis.__GLUON_SETTINGS__;g.autoMac32=g.effectiveMac32=v;s.textContent=g.status();try{globalThis.localStorage?.setItem(\"gluon.mac32.changed\",(v?\"1:\":\"0:\")+Date.now())}catch{}}" \
    "catch{t.checked=!v;s.textContent=\"The setting could not be saved. Please try again.\"}finally{t.disabled=false}}})," \
    "J(\"span\",{children:\"Use Gluon for 32-bit Mac games\"})]})," \
    "J(\"p\",{style:{opacity:.75,lineHeight:1.5,margin:\"10px 0 0 28px\"},children:" \
    "\"Automatically use the Windows version when a game's Mac version is 32-bit. 64-bit Mac games keep their native version.\"})," \
    "J(\"p\",{role:\"status\",\"aria-live\":\"polite\",style:{marginLeft:28},children:globalThis.__GLUON_SETTINGS__.status()})," \
    "globalThis.__GLUON_SETTINGS__.renderPreload(J)]});\n" \
    "globalThis.__GLUON_SETTINGS__.renderPreload=J=>J(\"div\",{style:{paddingTop:12},children:[" \
    "J(\"label\",{style:{display:\"flex\",alignItems:\"center\",gap:12,cursor:\"pointer\"},children:[" \
    "J(\"input\",{type:\"checkbox\",role:\"switch\",name:\"gluon_preload_wine\",defaultChecked:globalThis.__GLUON_SETTINGS__.preloadWine," \
    "onChange:async e=>{const t=e.currentTarget,v=t.checked,g=globalThis.__GLUON_SETTINGS__,s=t.closest(\"div\").querySelector(\"[role=status]\");" \
    "t.disabled=true;try{const f=g.specifyVerified||g.specify||(typeof globalThis.SteamClient?.Apps?.SpecifyCompatTool===\"function\"?n=>SteamClient.Apps.SpecifyCompatTool(0,n):null);" \
    "if(!f)throw Error();const r=await f(v?\"__gluon_settings_preload_on_v1\":\"__gluon_settings_preload_off_v1\");" \
    "if(r===false||r?.success===false)throw Error();g.preloadWine=v;s.textContent=\"\";" \
    "try{globalThis.localStorage?.setItem(\"gluon.preload.changed\",(v?\"1:\":\"0:\")+Date.now())}catch{}}" \
    "catch{t.checked=!v;s.textContent=\"The setting could not be saved. Please try again.\"}finally{t.disabled=false}}})," \
    "J(\"span\",{children:\"Preload Wine\"})]})," \
    "J(\"p\",{style:{opacity:.85,lineHeight:1.5,margin:\"10px 0 0 28px\"},children:" \
    "\"Warm the Windows runtime in the background when Steam opens for a faster first Play.\"})," \
    "J(\"p\",{role:\"status\",\"aria-live\":\"polite\",style:{marginLeft:28}})]});\n" \
    "if(typeof globalThis.addEventListener===\"function\"&&!globalThis.__GLUON_SETTINGS__.listeningPreload){" \
    "globalThis.__GLUON_SETTINGS__.listeningPreload=true;globalThis.addEventListener(\"storage\",e=>{" \
    "if(e.key!==\"gluon.preload.changed\"||!e.newValue)return;const g=globalThis.__GLUON_SETTINGS__;" \
    "g.preloadWine=e.newValue.startsWith(\"1:\");const t=globalThis.document?.querySelector('input[name=gluon_preload_wine]');if(t)t.checked=g.preloadWine})}\n" \
    "globalThis.__GLUON_SETTINGS__.macOnlyLabel=(J,id)=>globalThis.__NOTPROTON_NATIVE_PLATFORM__?.mac32Only?.has(id)?" \
    "J(\"p\",{style:{color:\"#aab5bf\",fontSize:13,lineHeight:1.4,margin:\"10px 24px\"},children:\"32-bit Mac only · Requires a legacy Mac runtime\"}):null;\n"
#endif
