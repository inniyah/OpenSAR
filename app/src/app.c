#include "app.h"

void StartupHook( void )
{
	printf("in %s().\n",__FUNCTION__);
#if defined(WIN32)
	Stmo_Init(&Stmo_ConfigData);
#endif    
}

void ShutdownHook( StatusType Error )
{
	printf("in %s().\n",__FUNCTION__);
}
void ErrorHook( StatusType Error )
{
	printf("in %s().\n",__FUNCTION__);
}
void PreTaskHook( void )
{
	printf("in %s().\n",__FUNCTION__);
}
void PostTaskHook( void )
{
	printf("in %s().\n",__FUNCTION__);
}

void Task10ms(void)
{
	for(;;)
	{
		printf("in %s().\n",__FUNCTION__);
		(void)WaitEvent(EVENT_MASK_EventTask10ms);

		(void)ClearEvent(EVENT_MASK_EventTask10ms);
	}
	TerminateTask();
}

void Task20ms(void)
{
	for(;;)
	{
		printf("in %s().\n",__FUNCTION__);
		(void)WaitEvent(EVENT_MASK_EventTask20ms);
		app_led_20ms_runnable();
		app_gauge_20ms_runnable();
		(void)ClearEvent(EVENT_MASK_EventTask20ms);
	}
	TerminateTask();
}
void Task100ms(void)
{
	for(;;)
	{
		printf("in %s().\n",__FUNCTION__);
		(void)WaitEvent(EVENT_MASK_EventTask100ms);
		//printf("Task100ms is running.\n");
		app_nvm_100ms_runnable();
		(void)ClearEvent(EVENT_MASK_EventTask100ms);
	}
	TerminateTask();
}

void TaskEvent(void)
{
	for(;;)
	{
		printf("in %s().\n",__FUNCTION__);
		(void)WaitEvent(EVENT_MASK_Event1000ms);
		app_led_1000ms_runnable();
		app_time_1000ms_runnable();
		(void)ClearEvent(EVENT_MASK_Event1000ms);
	}
	TerminateTask();
}

